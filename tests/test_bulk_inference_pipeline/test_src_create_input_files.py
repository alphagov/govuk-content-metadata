import pytest
from unittest import mock
from bulk_inference_pipeline.src.create_input_files import write_query


@pytest.fixture
def mock_client():
    with mock.patch("google.cloud.bigquery.Client") as MockClass:
        yield MockClass.return_value


def test_write_query(mock_client):
    # Define the test variables
    sql_query = "SELECT * FROM my_table"
    dest_project = "my_project"
    dest_dataset = "my_dataset"
    dest_table = "my_table"

    # Mock the Google BigQuery objects
    query_job_mock = mock_client.query.return_value
    query_job_mock.result.return_value = "SUCCESS"

    # Call the function and assert the return value
    assert (
        write_query(mock_client, sql_query, dest_project, dest_dataset, dest_table)
        == "SUCCESS"
    )

    # Assert that the function called the expected Google BigQuery methods with the expected arguments
    mock_client.query.assert_called_once_with(sql_query, job_config=mock.ANY)
    job_config = mock_client.query.call_args[1]["job_config"]
    assert str(job_config.destination) == f"{dest_project}.{dest_dataset}.{dest_table}"
    assert job_config.write_disposition == "WRITE_TRUNCATE"
    query_job_mock.result.assert_called_once()
