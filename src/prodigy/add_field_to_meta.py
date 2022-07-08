# This script is designed to add a field to the metadata of annotations for .jsonl file
# The purpose initially arose because earlier annotations did not have a 'base_path' field in the metadata,
# meaning that scripts such as `get_confusion_matrix.py` could not run.

import json
import jsonlines


def add_field_to_meta(in_file, out_file):
    """
    This function takes a .jsonl file for Prodigy as input, and adds 'Unknown' to the 'base_path' meta if
    there is no 'base_path' present.
    Args:
        in_file: dataset as a .jsonl file,
        out_file: dataset location for .jsonl
    Returns:
        .jsonl file with completed 'base_path' field.
    """

    examples = []

    with jsonlines.open(in_file) as f:
        for line in f.iter():
            # print(line)
            examples.append(line)

    # if 'base_path' not in 'meta', add 'Unknown' base path
    for e in examples:
        if "meta" in e:
            if "base_path" in e["meta"]:
                continue
            elif "base_path" not in e["meta"]:
                e["meta"]["base_path"] = "Unknown"

    with open(out_file, "w") as outfile:
        for entry in examples:
            json.dump(entry, outfile)
            outfile.write("\n")


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

    add_field_to_meta(in_file=argparse_args.in_file, out_file=argparse_args.out_file)
