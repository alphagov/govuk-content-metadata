"""
This script contains a function that is used for wrangling outputs into format for Neo4j ingestion.
"""

# import argparse
import csv
import json
import re
from collections import OrderedDict
import os
import pandas as pd
import glob
from functools import reduce
import unicodedata as ud


# path from downloaded s3 files and path to processed folder to save to
download_path = (
    "/Users/roryhurley/Documents/GitHub/govuk-content-metadata/data/download"
)
processed_path = (
    "/Users/roryhurley/Documents/GitHub/govuk-content-metadata/data/processed"
)


def jsonl_to_csv_wrangle(in_jsonl, out_jsonl):
    """_summary_

    :param in_jsonl: Input .jsonl file
    :type in_jsonl: JSONL
    :param out_jsonl: Output .jsonl file
    :type out_jsonl: JSONL
    :raises ValueError: ValueErrory if none of ['title', 'description', 'text'] in title of `in_jsonl`"
    """
    unit = re.findall(r"title|description|text", in_jsonl)
    if unit:
        unit = unit[0]
    else:
        raise ValueError(
            "Input file must have ['title, 'description', 'text'] in title."
        )
    # MAIN FUNCTION
    with open(out_jsonl, "w") as f:
        write = csv.writer(f, delimiter=",")
        write.writerow(["base_path", "entity_inst", "entity_type", f"{unit}_weight"])
        for line in open(in_jsonl):
            test_ex_json = json.loads(line)
            base_path = list(test_ex_json.keys())[0]
            entities = list(test_ex_json.values())[0]
            ents = [(i[0], i[1]) for i in entities]
            ents = [(i[0], i[1], ents.count(i)) for i in ents]
            ents = list(OrderedDict.fromkeys(ents))
            out = [[base_path, ent[0], ent[1], ent[2]] for ent in ents]
            write.writerows(out)


# for each file in the downloaded path, process...
for i in os.listdir(download_path):
    in_file = os.path.join(download_path, i)
    base_name = os.path.basename(in_file).split(".")[0]
    print(base_name)
    jsonl_to_csv_wrangle(
        in_jsonl=in_file,
        out_jsonl=os.path.join(processed_path, "processed_{}.csv".format(base_name)),
    )

# load each files as a dataframe and concatenate into one, save to csv
path = processed_path  # use your path
all_files = glob.glob(os.path.join(path, "*.csv"))
li = []
for filename in all_files:
    df = pd.read_csv(filename, index_col=None, header=0)
    li.append(df)
frame = pd.concat(li, axis=0, ignore_index=True)
print(frame.shape)
# save frame to csv
frame.to_csv(
    "/Users/roryhurley/Documents/GitHub/govuk-content-metadata/data/for_merge/all_text.csv",
    index=None,
)

# load concatednated files separately,
df_titles = pd.read_csv(
    "/Users/roryhurley/Documents/GitHub/govuk-content-metadata/data/for_merge/all_titles.csv",
    encoding="utf-8",
)
df_descriptions = pd.read_csv(
    "/Users/roryhurley/Documents/GitHub/govuk-content-metadata/data/for_merge/all_descriptions.csv",
    encoding="utf-8",
)
df_text = pd.read_csv(
    "/Users/roryhurley/Documents/GitHub/govuk-content-metadata/data/for_merge/all_text.csv",
    encoding="utf-8",
)
# sort each by base_path
df_titles = df_titles.sort_values(by=["base_path"], ascending=True)
df_descriptions = df_descriptions.sort_values(by=["base_path"], ascending=True)
df_text = df_text.sort_values(by=["base_path"], ascending=True)

# merge all dataframes
merge_df = reduce(
    lambda x, y: pd.merge(
        x, y, on=["base_path", "entity_inst", "entity_type"], how="outer"
    ),
    [df_titles, df_descriptions, df_text],
)

# force columns to string type
merge_df["base_path"] = merge_df["base_path"].astype(str)
merge_df["entity_inst"] = merge_df["entity_inst"].astype(str)
merge_df["entity_type"] = merge_df["entity_type"].astype(str)

# force columns to lower case
merge_df["entity_inst"] = merge_df["entity_inst"].str.lower()
merge_df["base_path"] = merge_df["base_path"].str.lower()


# functions to filter out erroneous names
def contains_alphanum(string: str) -> bool:
    return any([c for c in string if c.isalnum()])


latin_letters = {}


def is_latin(uchr):
    try:
        return latin_letters[uchr]
    except KeyError:
        return latin_letters.setdefault(uchr, "LATIN" in ud.name(uchr))


def only_roman_chars(unistr):
    return all(is_latin(uchr) for uchr in unistr if uchr.isalpha())


# use functions to extract flag erroneous names
merge_df["inst_has_alphanum"] = [
    contains_alphanum(line) for line in merge_df["entity_inst"]
]
merge_df["only_roman_chars"] = merge_df["entity_inst"].apply(
    lambda x: only_roman_chars(x)
)

# fill missing values with na
merge_df = merge_df.fillna(0)

# # filter any erroneous names
# merge_df = merge_df[merge_df["inst_has_alphanum"] == True]
# merge_df = merge_df[merge_df["only_roman_chars"] == True]

# make entity instance lower case
merge_df["entity_inst"] = merge_df["entity_inst"].str.lower()

# create new field by combining instance and type
merge_df["entity_combo"] = merge_df["entity_inst"] + merge_df["entity_type"]

# create a unique has for each entity combo
merge_df["entity_hash"] = merge_df["entity_combo"].apply(lambda x: hash(x))

# save to file
merge_df.to_csv(
    "/Users/roryhurley/Documents/GitHub/govuk-content-metadata/data/for_merge/test.csv",
    index=None,
)

# load this file
df_master = pd.read_csv(
    "/Users/roryhurley/Documents/GitHub/govuk-content-metadata/data/for_merge/test.csv"
)

# drop fields not needed
df_master = df_master.drop(
    ["inst_has_alphanum", "only_roman_chars", "entity_combo"], axis=1
)

# calculate total weight across all units
df_master["total_weight"] = (
    df_master["title_weight"]
    + df_master["description_weight"]
    + df_master["text_weight"]
)

# save to csv
df_master.to_csv(
    "/Users/roryhurley/Documents/GitHub/govuk-content-metadata/data/for_merge/ner_phase1_roberta_entities.csv",
    index=None,
)


# if __name__ == "__main__":

#     argparser = argparse.ArgumentParser(description="Run src.prodigy.binary_to_json")

#     # Define the positional arguments we want to get from the user
#     argparser.add_argument(
#         "-in_jsonl",
#         type=str,
#         action="store",
#         required=True,
#         help="Input jsonl file.",
#     )

#     argparser.add_argument(
#         "-out_jsonl",
#         type=str,
#         action="store",
#         required=True,
#         help="Output jsonl file.",
#     )

#     argparser_args = argparser.parse_args()

#     jsonl_to_govgraph(argparser_args.in_jsonl, argparser_args.out_jsonl)
