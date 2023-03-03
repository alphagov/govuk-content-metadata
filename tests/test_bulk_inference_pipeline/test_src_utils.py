import pytest
from unittest.mock import Mock, MagicMock, patch
from google.cloud import bigquery
import types
import gzip
from io import BytesIO
import os

from bulk_inference_pipeline.src.utils import (
    stream_from_bigquery,
    chunks,
    parse_sql_script,
    upload_to_bucket,
)


def test_stream_from_bigquery():
    # create a mock bigquery client
    mock_client = Mock(spec=bigquery.client.Client)

    # create some test data
    test_data = [("test", 1, "example.com"), ("another test", 2, "example.com")]

    # create a mock query job with the test data
    mock_query_job = MagicMock()
    mock_query_job.__iter__.return_value = iter(test_data)
    mock_query_job.result.return_value = iter(test_data)

    # mock the bigquery query method to return the mock query job
    mock_client.query.return_value = mock_query_job

    # call the function with a test query
    query = "SELECT * FROM mytable"
    results = list(stream_from_bigquery(query, mock_client))

    # check that the function returned the expected results
    assert results == [("test", 1, "example.com"), ("another test", 2, "example.com")]


def test_chunks_output_type_1():
    """Assert output of chunks() is a generator"""
    input_generator = (x for x in range(0, 20))
    output_generators = chunks(input_generator, size=5)
    assert isinstance(output_generators, types.GeneratorType)


def test_chunks_output_type_2():
    """Assert output of chunks() is a generator of generators"""
    input_generator = (x for x in range(0, 20))
    output_generators = chunks(input_generator, size=5)
    assert isinstance(next(output_generators), types.GeneratorType)


def test_chunks_is_correct():
    """Assert output of chunks() is correct"""
    input_generator = (x for x in range(0, 18))
    output_generators = chunks(input_generator, size=5)
    assert list(next(output_generators)) == [0, 1, 2, 3, 4]
    assert list(next(output_generators)) == [5, 6, 7, 8, 9]
    assert list(next(output_generators)) == [10, 11, 12, 13, 14]
    assert list(next(output_generators)) == [15, 16, 17]


# mock a gzipped csv file
mock_rows_byte = b"title\ttext\tstuff\tid\n\
    This is a title\tSome text.\t9876\tbase_path1\n\
    And a second title\tMore text!\t1234\tbase_path2"


@pytest.fixture()
def in_memory_gzipped_csv():
    stream = BytesIO()
    with gzip.open(stream, "wb") as f:
        f.write(mock_rows_byte)
    # Seek back to the beginning of the file
    stream.seek(0)
    return stream


@pytest.fixture
def sample_sql_script(tmpdir):
    # Create a sample SQL script
    sql_script = """SELECT * FROM my_table;"""
    filepath = os.path.join(tmpdir, "test.sql")
    with open(filepath, "w") as f:
        f.write(sql_script)
    return filepath


def test_parse_sql_script(sample_sql_script):
    # Ensure that the function returns the contents of the SQL script
    assert parse_sql_script(sample_sql_script) == "SELECT * FROM my_table;"

    # Ensure that the function raises a FileNotFoundError if the file does not exist
    with pytest.raises(FileNotFoundError):
        parse_sql_script("non_existent_file.sql")


@pytest.fixture
def mock_storage_client():
    with patch("google.cloud.storage.Client") as MockClass:
        yield MockClass.return_value


def test_upload_to_bucket(mock_storage_client):
    # Define the test variables
    bucket_name = "my_bucket"
    blob_name = "subfolder/test_file.txt"
    path_to_local_file = "test_file.txt"

    # Mock the Google Storage bucket and blob objects
    bucket_mock = mock_storage_client.get_bucket.return_value
    blob_mock = bucket_mock.blob.return_value

    # Call the function and assert the return value
    assert (
        upload_to_bucket(
            mock_storage_client, bucket_name, blob_name, path_to_local_file
        )
        == blob_mock.public_url
    )

    # Assert that the blob is uploaded from the local file
    blob_mock.upload_from_filename.assert_called_once_with(path_to_local_file)

    # Assert that the function called the expected Google Storage methods with the expected arguments
    mock_storage_client.get_bucket.assert_called_once_with(bucket_name)
    bucket_mock.blob.assert_called_once_with(blob_name)
