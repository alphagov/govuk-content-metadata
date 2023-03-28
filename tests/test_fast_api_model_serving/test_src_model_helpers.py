from unittest.mock import MagicMock
from fast_api_model_serving.src.model_helpers import combine_ner_components


def test_combine_ner_components_replace_listeners():
    # Create two mocked spacy pipeline objects
    ner_trf1 = MagicMock()
    ner_trf1.pipe_names = ["transformer", "ner"]
    ner_trf2 = MagicMock()
    ner_trf2.pipe_names = ["transformer", "ner"]

    # Mock replace_listeners method and call the function
    ner_trf2.replace_listeners = MagicMock()
    _ = combine_ner_components(ner_trf1, ner_trf2)

    # Assert that replace_listeners was called with the expected arguments
    ner_trf2.replace_listeners.assert_called_with(
        "transformer", "ner", ["model.tok2vec"]
    )


def test_combine_ner_components_add_pipe():
    # Create two mocked spacy pipeline objects
    ner_trf1 = MagicMock()
    ner_trf1.pipe_names = ["transformer", "ner"]
    ner_trf2 = MagicMock()
    ner_trf2.pipe_names = ["transformer", "ner"]

    # Mock add_pipe method and call the function
    ner_trf1.add_pipe = MagicMock()
    _ = combine_ner_components(ner_trf1, ner_trf2)

    # Assert that add_pipe was called with the expected arguments
    ner_trf1.add_pipe.assert_called_with(
        "ner", name="ner_2", source=ner_trf2, before="ner"
    )
