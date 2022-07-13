import pytest
from src.prodigy.get_confusion_matrix import confusion_matrix
import spacy

nlp = spacy.load("en_core_web_lg")
doc1 = nlp("Find full or part-time jobs in England, Scotland and Wales.")
doc2 = nlp("Paul Smith can be reached on 17 August 2022.")

args_correct_eval = (
    {
        "text": "Find full or part-time jobs in England, Scotland and Wales.",
        "spans": [
            {"start": 31, "end": 38, "text": "England", "label": "GPE"},
            {"start": 40, "end": 48, "text": "Scotland", "label": "GPE"},
            {"start": 53, "end": 58, "text": "Wales", "label": "GPE"},
        ],
        "_input_hash": 1234,
        "_task_hash": 789,
        "meta": {"base_path": "govuk/abc"},
    },
    {
        "text": "Paul Smith can be reached on 17 August 2022.",
        "spans": [
            {"start": 0, "end": 10, "text": "Paul Smith", "label": "PERSON"},
            {"start": 29, "end": 43, "text": "17 August 2022", "label": "DATE"},
        ],
        "_input_hash": 345,
        "_task_hash": 789,
        "meta": {"base_path": "govuk/xyz"},
    },
)

args_incorrect_eval = (
    {
        "text": "Find full or part-time jobs in England, Scotland and Wales.",
        "spans": [
            {"start": 31, "end": 38, "text": "England", "label": "ORG"},
            {"start": 40, "end": 48, "text": "Scotland", "label": "GPE"},
            {"start": 53, "end": 58, "text": "Wales", "label": "GPE"},
        ],
        "_input_hash": 1234,
        "_task_hash": 789,
        "meta": {"base_path": "govuk/abc"},
    },
    {
        "text": "Paul Smith can be reached on 17 August 2022.",
        "spans": [
            {"start": 5, "end": 10, "text": "Paul Smith", "label": "PERSON"},
            {"start": 29, "end": 43, "text": "17 August 2022", "label": "DATE"},
        ],
        "_input_hash": 345,
        "_task_hash": 789,
        "meta": {"base_path": "govuk/xyz"},
    },
)


correct_out = ([], [])
incorrect_out = (
    [
        (
            doc1,
            ("England", 31, 38, "GPE"),
            [
                ("England", 31, 38, "ORG"),
                ("Scotland", 40, 48, "GPE"),
                ("Wales", 53, 58, "GPE"),
            ],
        ),
        (
            doc2,
            ("Paul Smith", 0, 10, "PERSON"),
            [("Smith", 5, 10, "PERSON"), ("17 August 2022", 29, 43, "DATE")],
        ),
    ],
    [
        (
            doc1,
            [
                ("England", 31, 38, "GPE"),
                ("Scotland", 40, 48, "GPE"),
                ("Wales", 53, 58, "GPE"),
            ],
            ("England", 31, 38, "ORG"),
        ),
        (
            doc2,
            [("Paul Smith", 0, 10, "PERSON"), ("17 August 2022", 29, 43, "DATE")],
            ("Smith", 5, 10, "PERSON"),
        ),
    ],
)

args_correct = [(args_correct_eval, correct_out)]
args_incorrect = [(args_incorrect_eval, incorrect_out)]


@pytest.mark.parametrize("correct_eval, correct_out", args_correct)
def test_correct_confusion_matrix(correct_eval, correct_out, en_core_web_lg):
    """Assert the ``confusion_matrix`` returns correctly."""
    assert confusion_matrix(correct_eval, en_core_web_lg) == correct_out


@pytest.mark.parametrize("incorrect_eval, incorrect_out", args_incorrect)
def test_incorrect_confusion_matrix(incorrect_eval, incorrect_out, en_core_web_lg):
    """Assert the ``confusion_matrix`` returns correctly."""
    assert (
        confusion_matrix(incorrect_eval, en_core_web_lg)[0][0][1]
        == incorrect_out[0][0][1]
    )
    assert (
        confusion_matrix(incorrect_eval, en_core_web_lg)[0][0][2]
        == incorrect_out[0][0][2]
    )
    assert (
        confusion_matrix(incorrect_eval, en_core_web_lg)[0][1][1]
        == incorrect_out[0][1][1]
    )
    assert (
        confusion_matrix(incorrect_eval, en_core_web_lg)[0][1][2]
        == incorrect_out[0][1][2]
    )
    assert (
        confusion_matrix(incorrect_eval, en_core_web_lg)[1][0][1]
        == incorrect_out[1][0][1]
    )
    assert (
        confusion_matrix(incorrect_eval, en_core_web_lg)[1][0][2]
        == incorrect_out[1][0][2]
    )
    assert (
        confusion_matrix(incorrect_eval, en_core_web_lg)[1][1][1]
        == incorrect_out[1][1][1]
    )
    assert (
        confusion_matrix(incorrect_eval, en_core_web_lg)[1][1][2]
        == incorrect_out[1][1][2]
    )
