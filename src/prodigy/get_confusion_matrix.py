"""
It produces an overview of False Positive and False Negative cases
(akin a confusion matrix) given an evaluation set and a NER model.

The script allows for the following positional arguments:

Args:
    ``--eval``: (required) The name of your evaluation data (without extension), as a stream JSONL object,
        the output of annotation with Prodigy. To be saved in the `data/gold` folder.
    ``--model``:   (required) The trained spacy best-model model, saved in the `models` folder.

To run the script from the root directory (change arguments accordingly):
```
    python -m src.prodigy.get_confusion_matrix --eval "rh_annotations_mark_goggepdm_2" --model-date "mark_goggepdm_2"
```

It returns two CSV files, saved under `data/interim`, containing the False Positive and False Negative cases.

"""


import os
import spacy
from typing import Union
import pandas as pd

from src.prodigy.utils import load_stream


def confusion_matrix(evaluation_data_jsonl: dict, ner_model) -> Union[list, list]:
    """
    Produces an overview of False Positive and False Negative cases
    (akin a confusion matrix) given an evaluation set and a NER model.

    Args:
        evaluation_data_jsonl: your evaluation data, as a stream jsonl object,
        the output of annotation with Prodigy.
        Each dictionary must contain a "text", and a "spans" keys.

        ner_model: a ner-model trained with spacy

    Return:
        Two lists: a list of false positive cases, and a list of false nagtaive cases.
    """

    fp_cases = []
    fn_cases = []

    data_tuples = [(eg["text"], eg) for eg in evaluation_data_jsonl]

    for doc, example in ner_model.pipe(data_tuples, as_tuples=True):

        correct_ents = [
            (doc.text[e["start"] : e["end"]], e["start"], e["end"], e["label"])
            for e in example["spans"]
        ]
        predicted_ents = [
            (
                doc.text[ent.start_char : ent.end_char],
                ent.start_char,
                ent.end_char,
                ent.label_,
            )
            for ent in doc.ents
        ]

        for ent in predicted_ents:
            if ent not in correct_ents:
                out = (doc, ent, correct_ents)
                fp_cases.append(out)

        for ent in correct_ents:
            if ent not in predicted_ents:
                out = (doc, predicted_ents, ent)
                fn_cases.append(out)

    return fp_cases, fn_cases


if __name__ == "__main__":

    import argparse
    from pathlib import Path

    confusion_parser = argparse.ArgumentParser(
        description="Run src.prodigy.get_confusion_matrix"
    )

    # Define the positional arguments we want to get from the user
    confusion_parser.add_argument(
        "-eval",
        type=str,
        action="store",
        dest="eval",
        required=True,
        help="Name of the JSNOL file with the human-generated evaluation cases",
    )

    confusion_parser.add_argument(
        "-model",
        type=str,
        action="store",
        dest="model",
        required=True,
        help="Name of the trained NER model",
    )

    confusion_args = confusion_parser.parse_args()

    OUPUT_DIR = Path(os.getenv("DIR_DATA_INTERIM"))
    MODEL_DIR = Path(os.getenv("DIR_MODELS"))
    INPUT_DIR = Path(os.getenv("DIR_DATA_GOLD"))

    # inputs
    EVAL_FILEPATH = INPUT_DIR.joinpath(confusion_args.eval + ".jsonl")
    MODELPATH = MODEL_DIR.joinpath(confusion_args.model, "model-best")

    jsonl_stream = load_stream(EVAL_FILEPATH)
    nlp_model_best = spacy.load(MODELPATH)

    # check that 'ner' is in pipelie
    assert "ner" in nlp_model_best.pipe_names

    fps, fns = confusion_matrix(jsonl_stream, nlp_model_best)

    # export
    fps_df = pd.DataFrame(fps).rename(
        columns={0: "text", 1: "false_positive", 2: "correct_all"}
    )
    fns_df = pd.DataFrame(fns).rename(
        columns={0: "text", 1: "predicted_all", 2: "false_negative"}
    )

    # outputs
    fps_out = OUPUT_DIR.joinpath(
        f"false_positives_model_{confusion_args.model}_eval_{confusion_args.eval}"
        + ".csv"
    )
    fns_out = OUPUT_DIR.joinpath(
        f"false_negatives_model_{confusion_args.model}_eval_{confusion_args.eval}"
        + ".csv"
    )

    fps_df.to_csv(fps_out)
    fns_df.to_csv(fns_out)
