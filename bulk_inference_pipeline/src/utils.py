import spacy
import json
from itertools import islice
from google.cloud import bigquery
from typing import Optional, Generator, Tuple

# Construct a BigQuery client object.
# BQ_CLIENT = bigquery.Client()
# STORAGE_CLIENT = storage.Client()


def load_model(path_to_model: str):
    return spacy.load(path_to_model)


def stream_from_bigquery(
    query: str, client: bigquery.client.Client
) -> Generator[Tuple[str, Optional[int], str], None, None]:
    query_job = client.query(query)
    for row in query_job:
        yield row


def write_output_from_stream(outfile: str, content_stream: Generator):
    """
    Writes outputs from a generator to JSONL format.

    NOTE: JSON does not preserve tuples and turn them into lists
    https://stackoverflow.com/questions/15721363/preserve-python-tuples-with-json
    """
    with open(outfile, "w") as f:
        for row in content_stream:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def chunks(iterable, size=10):
    """
    Splits a generator into chunks without pre-walking it. Each chunk is a generator.

    Args:
        iterable: the generator to be splitted
        size: number of elements in each chunk (default, 10)

    Returns:
        A generator of generators (the chunks)

    Ref: https://python.tutorialink.com/split-a-generator-into-chunks-without-pre-walking-it/
    """

    for first in iterable:  # stops when iterator is depleted

        def chunk():  # construct generator for next chunk
            yield first  # yield element from for loop
            for more in islice(iterable, size - 1):
                yield more  # yield more elements from the iterator

        yield chunk()  # in outer generator, yield next chunk


def parse_sql_script(filepath: str) -> str:
    """Parse a SQL script directly from the `folder` folder.
    Args:
        filepath: The full file path of the SQL script.
    Returns:
        A string of the parsed SQL script.
    """
    # Open `filename` in the `folder` folder, and read it
    with open(filepath, "r") as f:
        return f.read()
