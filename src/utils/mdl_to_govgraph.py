"""
This script contains a function that is used for wrangling outputs into format for Neo4j ingestion.
"""

from collections import OrderedDict
import re
import json


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
            json_list = list(json_file)
            for json_str in json_list:
                result = json.loads(json_str)
                base_path = result.keys()[0]
                entities = result.values()[0]
                ents = [(i[0], i[1]) for i in entities]
                ents = [(i, ents.count(i)) for i in ents]
                ents = list(OrderedDict.fromkeys(ents))
                ents = [
                    {"entity_name": j[0], "entity_type": j[1], "weight": k}
                    for (j, k) in ents
                ]
                out = {"base_path": base_path, "entities": ents}
                json.dump(out, outfile)
                outfile.write("\n")
