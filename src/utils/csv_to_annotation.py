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


def excel_to_df(excel_file) -> pd.DataFrame:
    """Converts an excel sheet with one or more tabs into a single DataFrame.

    Args:
        excel_file (_type_): A .xlsx file.

    Returns:
        pd.DataFrame: Concatenated DataFrame of the tab(s).
    """
    df = pd.read_excel(excel_file)
    return df


def csv_to_df(csv_file) -> pd.DataFrame:
    """Converts an excel sheet with one or more tabs into a single DataFrame.

    Args:
        excel_file (_type_): A .xlsx file.

    Returns:
        pd.DataFrame: Concatenated DataFrame of the tab(s).
    """
    df = pd.read_csv(csv_file)
    return df


def df_to_annotation_set(dataframe, outfile) -> json:
    """Converts rows of a DataFrame into Prodiogy annotataion format.

    Args:
        dataframe (_type_): DataFrame
        outfile (_type_): .JSONL file

    Returns:
        json: .JSONL file
    """
    with open(outfile, "w") as file:
        for i, val in dataframe.iterrows():
            pattern = {
                "text": str(val["line"]),
                "meta": {
                    "url": val["url"],
                    "line_number": val["line_number"],
                    "regex_or_rand": val["regex_or_rand"],
                    "cat": val["cat"],
                },
            }
            print(pattern)
            file.write(json.dumps(pattern))
            file.write("\n")


if __name__ == "__main__":

    # Create the parser
    parser = argparse.ArgumentParser()
    # Add an argument
    parser.add_argument("--csv_file", type=str, required=True)
    parser.add_argument("--out_file", type=str, required=True)

    # Parse the argument
    args = parser.parse_args()
    df = csv_to_df(args.csv_file)
    df_to_annotation_set(df, args.out_file)
