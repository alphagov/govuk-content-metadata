import pytest
from google.cloud import bigquery
from unittest.mock import MagicMock, Mock, patch
import spacy
import json
from typing import Generator
from bulk_inference_pipeline.src.extract_entities_cloud import (
    stream_rows_from_bigquery,
    extract_entities_pipe_from_tuples_to_dict,
    write_output_from_stream,
    load_model,
    make_inference,
)


@pytest.fixture
def client():
    # Create a mock BigQuery client object
    return MagicMock(spec=bigquery.Client)


def test_stream_rows_from_bigquery_text(client):
    # Define inputs for the function
    query = "SELECT line, url, line_number FROM my_table"
    part_of_page = "text"

    # Create mock QueryJob object with rows
    mock_query_job = MagicMock()
    mock_query_job.__iter__.return_value = [
        {"line": "line 1", "url": "url 1", "line_number": 1},
        {"line": "line 2", "url": "url 2", "line_number": 2},
    ]
    client.query.return_value = mock_query_job

    # Call the function with the inputs
    results = list(stream_rows_from_bigquery(query, client, part_of_page))

    # Assert that the function returns the expected results
    expected_results = [
        ("line 1", ("url 1", 1)),
        ("line 2", ("url 2", 2)),
    ]
    assert results == expected_results


def test_stream_rows_from_bigquery_title(client):
    # Define inputs for the function
    query = "SELECT title, url FROM my_table"
    part_of_page = "title"

    # Create mock QueryJob object with rows
    mock_query_job = MagicMock()
    mock_query_job.__iter__.return_value = [
        {"title": "title 1", "url": "url 1"},
        {"title": "title 2", "url": "url 2"},
    ]
    client.query.return_value = mock_query_job

    # Call the function with the inputs
    results = list(stream_rows_from_bigquery(query, client, part_of_page))

    # Assert that the function returns the expected results
    expected_results = [
        ("title 1", ("url 1")),
        ("title 2", ("url 2")),
    ]
    assert results == expected_results


def test_stream_rows_from_bigquery_description(client):
    # Define inputs for the function
    query = "SELECT description, url FROM my_table"
    part_of_page = "description"

    # Create mock QueryJob object with rows
    mock_query_job = MagicMock()
    mock_query_job.__iter__.return_value = [
        {"description": "description 1", "url": "url 1"},
        {"description": "description 2", "url": "url 2"},
    ]
    client.query.return_value = mock_query_job

    # Call the function with the inputs
    results = list(stream_rows_from_bigquery(query, client, part_of_page))

    # Assert that the function returns the expected results
    expected_results = [
        ("description 1", ("url 1")),
        ("description 2", ("url 2")),
    ]
    assert results == expected_results


ner_model = spacy.load("en_core_web_md")


def test_extract_entities_pipe_from_tuples_to_dict_text():
    # Setup
    rows = [("Rome was not built in a day but Paris ye.", ("https://example.com", 1))]
    b = 1
    n = 1
    part_of_page = "text"

    # Exercise
    output = list(
        extract_entities_pipe_from_tuples_to_dict(rows, ner_model, b, n, part_of_page)
    )

    # Verify
    expected_output = [
        {
            "url": "https://example.com",
            "entities": [
                {"name": "Rome", "type": "GPE", "start": 0, "end": 4},
                {"name": "a day", "type": "DATE", "start": 22, "end": 27},
                {"name": "Paris", "type": "GPE", "start": 32, "end": 37},
            ],
            "line_number": 1,
        }
    ]
    assert output == expected_output


def test_extract_entities_pipe_from_tuples_to_dict_no_etities():
    # Setup
    rows = [("There is nothing here.", ("https://example.com"))]
    b = 1
    n = 1
    part_of_page = "title"

    # Exercise
    output = list(
        extract_entities_pipe_from_tuples_to_dict(rows, ner_model, b, n, part_of_page)
    )

    # Verify
    expected_output = [{"url": "https://example.com", "entities": []}]
    assert output == expected_output


def test_write_output_from_stream(tmp_path):
    # Define test data
    data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
    expected_output = "".join(
        [json.dumps(row, ensure_ascii=False) + "\n" for row in data]
    )

    # Write data to a generator
    def data_generator() -> Generator:
        for row in data:
            yield row

    # Write generator output to file
    output_file = tmp_path / "output.jsonl"
    write_output_from_stream(str(output_file), data_generator())

    # Check if file contents are as expected
    with open(output_file, "r") as f:
        assert f.read() == expected_output


def test_load_model(tmp_path):
    # create a temporary test model to load
    nlp = spacy.blank("en")
    nlp.add_pipe("tagger")
    nlp.add_pipe("parser")

    # Your code Here
    model_path = tmp_path / "test_model"
    nlp.to_disk(model_path)

    # load the model using the function
    loaded_model = load_model(model_path)

    # check that the loaded model has the correct components
    assert len(loaded_model.pipeline) == 3
    assert loaded_model.has_pipe("tagger")
    assert loaded_model.has_pipe("parser")
    assert loaded_model.has_pipe("doc_cleaner")

    # remove the temporary test model
    nlp.from_disk(model_path, exclude=["tagger", "parser"])


# integration tests


@patch(
    "bulk_inference_pipeline.src.extract_entities_cloud.extract_entities_pipe_from_tuples_to_dict"
)
@patch("bulk_inference_pipeline.src.extract_entities_cloud.write_output_from_stream")
def test_make_inference(mock_write_output, mock_extract_entities):
    # create some test data
    rows = [
        ("This is a test.", ("test.com", 1)),
        ("Another test here.", ("test.com", 2)),
    ]
    ner_model = Mock()
    b = 1
    n = 1
    part_of_page = "text"
    outfile = "test.jsonl"

    # call the function with the test data
    make_inference(rows, ner_model, b, n, part_of_page, outfile)

    # check that the function called the mocked dependencies with the correct arguments
    mock_extract_entities.assert_called_once_with(
        rows=rows, ner_model=ner_model, b=b, n=n, part_of_page=part_of_page
    )
    mock_write_output.assert_called_once_with(
        outfile, mock_extract_entities.return_value
    )
