"""
This script contains a function that is used for wrangling outputs into format for Neo4j ingestion.
"""

from collections import OrderedDict
import re
import json
import argparse


# list_wrangle(in_list)
def list_wrangle(dict_list):
    """Wrangles input dictionaries into list of dictionaries for Neo4j.

    :param dict_list: List of input dictionaries.
    :type dict_list: List
    :return: List of output dictionaries.
    :rtype: List
    """
    outs = []
    for d in dict_list:
        result = d
        base_path = list(result.keys())[0]
        entities = list(result.values())[0]
        ents = [(i[0], i[1]) for i in entities]
        ents = [(i, ents.count(i)) for i in ents]
        ents = list(OrderedDict.fromkeys(ents))
        ents = [
            {"entity_name": j[0], "entity_type": j[1], "weight": k} for (j, k) in ents
        ]
        out = {"base_path": base_path, "entities": ents}
        outs.append(out)
    return outs


def jsonl_to_govgraph(in_jsonl, out_jsonl):
    """Wrangles input jsonl file into Neo4j output.

    :param in_jsonl: input jsonl file
    :type in_jsonl: .jsonl
    :param out_jsonl: output jsonl file
    :type out_jsonl: .jsonl
    :raises ValueError: Raise if ['title, 'description', 'text'] not in in_file
    """
    unit = re.findall(r"title|description|text", in_jsonl)
    if unit:
        unit = unit[0]
    else:
        raise ValueError(
            "Input file must have ['title, 'description', 'text'] in title."
        )
    with open(out_jsonl, "w") as outfile:
        with open(in_jsonl, "r") as json_file:
            json_str_list = list(json_file)
            json_list = [json.loads(i) for i in json_str_list]
            wrangle_list = list_wrangle(json_list)
            for entry in wrangle_list:
                json.dump(entry, outfile)
                outfile.write("\n")


if __name__ == "__main__":

    argparser = argparse.ArgumentParser(description="Run src.prodigy.binary_to_json")

    # Define the positional arguments we want to get from the user
    argparser.add_argument(
        "-in_jsonl",
        type=str,
        action="store",
        required=True,
        help="Input jsonl file.",
    )

    argparser.add_argument(
        "-out_jsonl",
        type=str,
        action="store",
        required=True,
        help="Output jsonl file.",
    )

    argparser_args = argparser.parse_args()

    jsonl_to_govgraph(argparser_args.in_jsonl, argparser_args.out_jsonl)
