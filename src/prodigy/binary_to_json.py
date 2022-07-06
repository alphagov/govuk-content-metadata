# this script is designed to convert from .spacy format back into .jsonl format
# this was done so that 'get_confusion_matrix.py' could be used easily from ./corpus

# To run:
# `python -m src.prodigy.binary_to_json -in_binary "./corpus/dev.spacy" -out_file "./data/gold/dev.jsonl"`

import json
import spacy
from spacy.tokens import DocBin


def binary_to_json(in_bin_file, out_json_file):
    nlp = spacy.blank("en")
    doc_bin = DocBin().from_disk(in_bin_file)
    examples = []  # examples in Prodigy's format
    for doc in doc_bin.get_docs(nlp.vocab):
        spans = [
            {"start": ent.start_char, "end": ent.end_char, "label": ent.label_}
            for ent in doc.ents
        ]
        examples.append({"text": doc.text, "spans": spans})

    with open(out_json_file, "w") as outfile:
        for entry in examples:
            json.dump(entry, outfile)
            outfile.write("\n")


if __name__ == "__main__":

    import argparse

    argparser = argparse.ArgumentParser(description="Run src.prodigy.binary_to_json")

    # Define the positional arguments we want to get from the user
    argparser.add_argument(
        "-in_binary",
        type=str,
        action="store",
        # dest="eval",
        required=True,
        help="The .spacy binary file.",
    )

    argparser.add_argument(
        "-out_file",
        type=str,
        action="store",
        # dest="model",
        required=True,
        help="Location to save the .jsonl file",
    )

    argparser_args = argparser.parse_args()

    binary_to_json(argparser_args.in_binary, argparser_args.out_file)
