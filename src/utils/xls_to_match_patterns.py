"""
This script converts a .xlsx file with one or more tabs, each with an 'EntityType' and 'SeedTerm' column, into a SpaCy .JSONL patterns file.
You must use arguments:
--excel_file: The input .xlsx file
--out_file: the location of the output JSONL file
--sheet_names: The sheet names
"""

import pandas as pd
import argparse
import json


def excel_to_df(excel_file: str, sheet_names: str) -> pd.DataFrame:
    """Converts an excel workbook with one or more sheets into a single DataFrame.

    Args:
        excel_file (_type_): path to a .xlsx file.
        sheet_names: names of excel sheets contained in excel_file that will be combined,
                     as one unique string with names separated by ,
                     Example: "name1,name2,name3"

    Returns:
        pd.DataFrame: Concatenated DataFrame of the sheet(s).
    """
    dfs = pd.read_excel(excel_file, sheet_name=[i for i in sheet_names])
    concat_dfs = pd.concat([dfs[i] for i in sheet_names])
    return concat_dfs


def df_to_match_patterns(dataframe: pd.DataFrame, outfile: str) -> json:
    """Converts rows of a DataFrame into Spacy match pattern format.

    Args:
        dataframe (_type_): a pandas DataFrame with columns 'EntityType' and 'SeedTerm'
        outfile (_type_): filepath to the .JSONL file

    Returns:
        json: .JSONL file
    """
    with open(outfile, "w") as file:
        for i, val in dataframe.iterrows():
            pattern_list = [{"LOWER": j.lower()} for j in val["SeedTerm"].split(" ")]
            pattern = {"label": val["EntityType"], "pattern": pattern_list}
            # pattern = {"label": val['EntityType'], "pattern":[{"lower": val['SeedTerm']}]}
            print(pattern)
            file.write(json.dumps(pattern))
            file.write("\n")


if __name__ == "__main__":

    # Create the parser
    parser = argparse.ArgumentParser()
    # Add an argument
    parser.add_argument("--excel_file", type=str, required=True)
    parser.add_argument("--sheet_names", type=str, required=True)
    parser.add_argument("--out_file", type=str, required=True)

    # Parse the argument
    args = parser.parse_args()
    sheet_names_list = args.sheet_names.split(",")
    print(sheet_names_list)
    df = excel_to_df(args.excel_file, sheet_names_list)
    df_to_match_patterns(df, args.out_file)
