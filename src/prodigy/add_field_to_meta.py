# This script is designed to add a field to the metadata of annotations for .jsonl file
# The purpose initially arose because earlier annotations did not have a 'base_path' field in the metadata,
# meaning that scripts such as `get_confusion_matrix.py` could not run.

import json
from src.prodigy.utils import load_stream


def add_field_to_meta(in_stream_list):
    """This function takes a JSONL stream as input, and adds 'Unknown' to the 'base_path' meta if
        there is no 'base_path' present.

    :param in_stream_list: Input jsonl stream
    :type in_stream_list: List
    :return: Input jsonl stream
    :rtype: List
    """
    out_lines = []
    for line in in_stream_list:
        if "meta" not in line:
            line["meta"] = {}
        if "meta" in line:
            if "base_path" in line["meta"]:
                out_lines.append(line)
            elif "base_path" not in line["meta"]:
                line["meta"]["base_path"] = "unknown"
                out_lines.append(line)
    return out_lines


if __name__ == "__main__":

    import argparse

    arg_parser = argparse.ArgumentParser(
        description="Run src.prodigy.add_field_to_metadata"
    )

    # Define the positional arguments we want to get from the user
    arg_parser.add_argument(
        "-in_file",
        type=str,
        action="store",
        dest="in_file",
        required=True,
        help="Name of the JSNOL file of the input dataset",
    )

    # Define the positional arguments we want to get from the user
    arg_parser.add_argument(
        "-out_file",
        type=str,
        action="store",
        dest="out_file",
        required=True,
        help="Name of the JSNOL file of the output dataset",
    )

    argparse_args = arg_parser.parse_args()

    jsonl_stream = load_stream(argparse_args.in_file)
    jsonl_stream_list = list(jsonl_stream)
    out_stream_list = add_field_to_meta(jsonl_stream_list)

    with open(argparse_args.out_file, "w") as outfile:
        for entry in out_stream_list:
            json.dump(entry, outfile)
            outfile.write("\n")
