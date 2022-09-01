"""
This script contains a function that is used for wrangling outputs into format for Neo4j ingestion.

TO RUN:
```
python src/utils/mdl_to_govgraph.py
-s3_bucket govuk-data-infrastructure-integration
-s3_folder knowledge-graph-static/entities_intermediate
-out_filepath /Users/roryhurley/Documents/GitHub/govuk-content-metadata/data/for_merge/ner_phase1_roberta_entities.csv
```
"""

# import argparse
import csv
import json
import re
from collections import Counter
from typing import Dict, List, Union
import os
import pandas as pd
import glob
from functools import reduce
import unicodedata as ud
from src.utils.helpers_aws import (
    assume_role_with_mfa,
    temporary_connect_to_s3,
    download_files_from_s3_folder,
)


def count_entity_occurrence(
    line: Dict[str, List[list]]
) -> List[List[Union[str, str, str, int]]]:
    """
    Counts the number of occurrences of each (entity string, entity tag) combination in input line,
    after lowercasing the entity string.

    Args:
        A line in a JSONL file, of the format {base_path: [[entity string, entity tag, start, end], [...]}

    Returns:
        A list of sublists, each sublist of the form [base_path, entity string, entity tag, number occurrences]
    """
    for base_path, entities_list in line.items():
        ents = [ent[:2] for ent in entities_list]
        c = Counter((inst.lower(), tag) for inst, tag in ents)
        return [[base_path, k[0], k[1], v] for k, v in c.items()]


def jsonl_to_csv_wrangle(in_jsonl, out_csv):
    """Converts .JSONL input into a format with number of occurrences of each combination of (entity_instance, entity_type)
    in each base_path".

    :param in_jsonl: Input .jsonl file
    :type in_jsonl: str
    :param out_csv: Output .csv file
    :type out_csv: str
    :raises ValueError: ValueErrory if none of ['title', 'description', 'text'] in title of `in_jsonl`"
    """
    unit = re.findall(r"title|description|text", in_jsonl)
    try:
        unit = unit[0]
    except IndexError:
        print(f"Invalid file name: '{in_jsonl}' is skipped.")

    with open(out_csv, "w") as f:
        write = csv.writer(f, delimiter=",")
        write.writerow(["base_path", "entity_inst", "entity_type", "{unit}_weight"])
        # for each row in jsonl, wrangle into correct format and save to csv
        for line in open(in_jsonl):
            input_dict = json.loads(line)
            try:
                write.writerows(count_entity_occurrence(input_dict))
            except json.JSONDecodeError:
                print(f"Could not process contents of file: {in_jsonl}")


def process_and_save_files(download_path, processed_path):
    """Process files from one location, and save in another.

    :param download_path: Path to files from S3.
    :type download_path: str
    :param processed_path: Path to processed files.
    :type processed_path: str
    """
    # for each file in the downloaded path, process...
    if not os.path.exists(processed_path):
        os.makedirs(processed_path)
    for i in os.listdir(download_path):
        in_file = os.path.join(download_path, i)
        base_name = os.path.basename(in_file).split(".")[0]
        # invoke `json_to_csv_wrangle` function
        jsonl_to_csv_wrangle(
            in_jsonl=in_file,
            out_csv=os.path.join(processed_path, f"processed_{base_name}.csv"),
        )


def concatenate_csv_per_unit(processed_path, concat_path):
    """Concatenates/merges files in the same folder and saves in new folder location.

    :param processed_path: Path to processed files
    :type processed_path: str
    :param concat_path: Path to saved conatenated files
    :type concat_path: str
    """
    if not os.path.exists(concat_path):
        os.makedirs(concat_path)
    # load each files as a dataframe and concatenate into one, save to csv
    all_files = glob.glob(os.path.join(processed_path, "*.csv"))
    for unit in ["title", "description", "text"]:
        unit_df = pd.DataFrame()
        for filename in all_files:
            if unit in filename:
                df = pd.read_csv(filename, index_col=None, header=0)
                unit_df = pd.concat([unit_df, df], axis=0, ignore_index=True)
        # save frame to csv
        unit_df.to_csv(os.path.join(concat_path, f"all_{unit}.csv"), index=None)


def load_merge_csv_files(title_path, description_path, text_path):
    """Loads files for each unit type in, and merges them, aggregating counts in the process.

    :param title_path: Path to title file.
    :type title_path: str
    :param description_path: Path to description file.
    :type description_path: str
    :param text_path: Path to text file.
    :type text_path: str
    :return: Merged, aggregated DataFrame
    :rtype: Pandas DataFrame
    """
    # load concatednated files separately,
    df_titles = pd.read_csv(title_path, encoding="utf-8")
    df_descriptions = pd.read_csv(description_path, encoding="utf-8")
    df_text = pd.read_csv(text_path, encoding="utf-8")

    # sort each by base_path
    df_titles = df_titles.sort_values(by=["base_path"], ascending=True)
    df_descriptions = df_descriptions.sort_values(by=["base_path"], ascending=True)
    df_text = df_text.sort_values(by=["base_path"], ascending=True)

    # merge all dataframes, aggregating counts per unit
    merge_df = reduce(
        lambda x, y: pd.merge(
            x, y, on=["base_path", "entity_inst", "entity_type"], how="outer"
        ),
        [df_titles, df_descriptions, df_text],
    )

    return merge_df


# functions to filter out erroneous names
def contains_alphanum(string):
    """Flag if any string characters are alphanumeric, including non-latin words

    :param string: Input string.
    :type string: str
    :return: Boolean.
    :rtype: bool
    """
    return any([c for c in string if c.isalnum()])


def is_latin(uchr):
    """Check to see if latter is latin.

    :param uchr: Charater.
    :type uchr: str
    :return: Boolean.
    :rtype: bool
    """
    latin_letters = {}
    try:
        return latin_letters[uchr]
    except KeyError:
        return latin_letters.setdefault(uchr, "LATIN" in ud.name(uchr))


def only_roman_chars(unistr):
    """Check if string contains only roman characters.

    :param unistr: Input string.
    :type unistr: str
    :return: Boolean.
    :rtype: bool
    """
    return all(is_latin(uchr) for uchr in unistr if uchr.isalpha())


def preprocess_merged_df(merge_df, outfile_path):
    """Takes in merged DataFrame, performs processing steps, such as converting data types, flagging non-alphanumeric/non-latin
    names, fill n/a with '0', hashing of unique names, and aggregation of counts.

    :param merge_df: Merged DataFrame.
    :type merge_df: Pandas DataFrame
    :param outfile_path: Path to output file.
    :type outfile_path: str
    """

    # force columns to string type
    merge_df["base_path"] = merge_df["base_path"].astype(str)
    merge_df["entity_inst"] = merge_df["entity_inst"].astype(str)
    merge_df["entity_type"] = merge_df["entity_type"].astype(str)

    # force columns to lower case
    merge_df["entity_inst"] = merge_df["entity_inst"].str.lower()
    merge_df["base_path"] = merge_df["base_path"].str.lower()

    # use helper functions to extract flag erroneous names
    merge_df["inst_has_alphanum"] = [
        contains_alphanum(line) for line in merge_df["entity_inst"]
    ]
    merge_df["only_roman_chars"] = merge_df["entity_inst"].apply(
        lambda x: only_roman_chars(x)
    )

    # fill missing values with na
    merge_df = merge_df.fillna(0)

    # filter any erroneous names
    merge_df = merge_df[merge_df["inst_has_alphanum"]]
    merge_df = merge_df[merge_df["only_roman_chars"]]

    # make entity instance lower case
    merge_df["entity_inst"] = merge_df["entity_inst"].str.lower()

    # create new field by combining instance and type
    merge_df["entity_combo"] = merge_df["entity_inst"] + merge_df["entity_type"]

    # create a unique has for each entity combo
    merge_df["entity_hash"] = merge_df["entity_combo"].apply(lambda x: hash(x))

    # drop fields not needed
    df_master = merge_df.drop(
        ["inst_has_alphanum", "only_roman_chars", "entity_combo"], axis=1
    )

    # calculate total weight across all units
    df_master["total_weight"] = (
        df_master["title_weight"]
        + df_master["description_weight"]
        + df_master["text_weight"]
    )

    # save to csv
    df_master.to_csv(outfile_path, index=None)


AWS_USERNAME = os.getenv("AWS_USERNAME")
AWS_DATASCIENCEUSERS_ACCOUNTID = os.getenv("AWS_DATASCIENCEUSERS_ACCOUNTID")
AWS_GDSUSER_ACCOUNTID = os.getenv("AWS_GDSUSER_ACCOUNTID")
AWS_DATASCIENCEUSERS_NAME = os.getenv("AWS_DATASCIENCEUSERS_NAME")


if __name__ == "__main__":

    creds = assume_role_with_mfa(
        username=AWS_USERNAME,
        user_account_id=AWS_GDSUSER_ACCOUNTID,
        role_account_id=AWS_DATASCIENCEUSERS_ACCOUNTID,
        role_name=AWS_DATASCIENCEUSERS_NAME,
    )

    import argparse

    argparser = argparse.ArgumentParser(description="Run src.utils.mdl_to_govgraph")
    # Define the positional arguments we want to get from the user
    argparser.add_argument(
        "-s3_bucket",
        type=str,
        action="store",
        required=True,
        help="S3 Bucket.",
    )
    argparser.add_argument(
        "-s3_folder",
        type=str,
        action="store",
        required=True,
        help="S3 Folder.",
    )
    argparser.add_argument(
        "-out_filepath",
        type=str,
        action="store",
        required=True,
        help="Output filepath.",
    )

    argparser_args = argparser.parse_args()

    print("Connecting to S3...")

    resource = temporary_connect_to_s3(creds)

    print("Connected to S3.")

    print("Downloading files from S3...")

    download_files_from_s3_folder(
        resource,
        s3_bucket=argparser_args.s3_bucket,
        folder_path=argparser_args.s3_folder,
        output_folder="/tmp/govuk-content-metadata/data/download",
    )

    print("Downloaded files from S3.")

    print("Processing and saving files...")

    process_and_save_files(
        download_path="/tmp/govuk-content-metadata/data/download",
        processed_path="/tmp/govuk-content-metadata/data/processed",
    )

    print("Processed and saved files.")

    print("Concatenating and saving files...")

    concatenate_csv_per_unit(
        processed_path="/tmp/govuk-content-metadata/data/processed",
        concat_path="/tmp/govuk-content-metadata/data/for_merge",
    )

    print("Concatenated and saved files.")

    print("Loading and merging files...")

    merge_df = load_merge_csv_files(
        title_path="/tmp/govuk-content-metadata/data/for_merge/all_title.csv",
        description_path="/tmp/govuk-content-metadata/data/for_merge/all_description.csv",
        text_path="/tmp/govuk-content-metadata/data/for_merge/all_text.csv",
    )

    print("Loaded and merging files.")

    print("Preprocessing data...")

    preprocess_merged_df(
        merge_df,
        outfile_path=argparser_args.out_filepath,
    )

    print("Data preprocessed.")
