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


def excel_to_df(excel_file, sheet_names) -> pd.DataFrame:
    """Converts an excel sheet with one or more tabs into a single DataFrame.

    Args:
        excel_file (_type_): A .xlsx file.

    Returns:
        pd.DataFrame: Concatenated DataFrame of the tab(s).
    """
    dfs = pd.read_excel(excel_file, sheet_name=[i for i in sheet_names])
    concat = pd.concat([dfs[i] for i in sheet_names])
    return concat


def df_to_match_patterns(dataframe, outfile) -> json:
    """Converts rows of a DataFrame into Spacy match pattern format.

    Args:
        dataframe (_type_): DataFrame
        outfile (_type_): .JSONL file

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
            # file.write(pattern)


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
