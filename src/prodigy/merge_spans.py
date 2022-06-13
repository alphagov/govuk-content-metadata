#not yet working, but WIP recipe of the prodigy_merge_annotation_spans.py script

import prodigy
from prodigy.components.db import connect
from prodigy.models.ner import merge_spans
from prodigy.util import split_string
from typing import List, Optional


@prodigy.recipe(
    "merge-spans",
    gold_dataset=("Dataset to save answers to", "positional", None, str),
    silver_datasets=("One or more comma-separated datasets", "option", "s", split_string),
    )

def merge_spans(
    gold_dataset: str, 
    silver_datasets: Optional[List[str]] = None,
):
    """
    docstrings
    """
    db = connect()

    if gold_dataset in db:
        raise ValueError("dataset {} already in db!".format(gold_dataset))
    
    for dataset in silver_datasets:
        if dataset not in db:
            raise ValueError("dataset {} not in db!".format(dataset))
        else:
            print("dataset {} in db!".format(dataset))

    examples = []
    for dataset in silver_datasets:
        print(dataset)
        examples += db.get_dataset(dataset)  # get examples from the database
    
    print(len(examples))

    merged_examples = merge_spans(examples)
    print(len(merged_examples))
    # db.add_dataset(dataset)

    # db.add_examples(merged_examples, datasets=[gold_dataset])


# db = connect()  # connect to the DB using the prodigy.json settings
# datasets = ['sample_form_at_first80', 'sample_form_rh_correct', 'forms_rh_at_3000']
# examples = []
# for dataset in datasets:
#     examples += db.get_dataset(dataset)  # get examples from the database

# merged_examples = merge_spans(examples)

# db.add_dataset('merged_dataset_script')

# db.add_examples(merged_examples, datasets=['merged_dataset_script'])

