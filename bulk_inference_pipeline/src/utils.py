import json
from itertools import islice
from google.cloud import bigquery, storage
from google.cloud.storage.fileio import BlobWriter
from typing import Optional, Generator, Tuple

# Construct a BigQuery client object.
# BQ_CLIENT = bigquery.Client()
# STORAGE_CLIENT = storage.Client()


def stream_from_bigquery(
    query: str, client: bigquery.client.Client
) -> Generator[Tuple[str, Optional[int], str], None, None]:
    query_job = client.query(query)
    for row in query_job:
        yield row


def upload_jsonl_from_stream(
    storage_client: storage.Client, bucket_name, stream_generator, destination_blob_name
):
    """
    Uploads bytes from a stream or other file-like object to a blob.
    Ref : https://cloud.google.com/storage/docs/streaming#stream_an_upload
    and https://stackoverflow.com/questions/44876235/uploading-a-json-to-google-cloud-storage-via-python
    and https://stackoverflow.com/questions/73687152/how-to-stream-upload-csv-data-to-google-cloud-storage-python
    """

    # Construct a client-side representation of the blob.
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    writer = BlobWriter(blob)

    # Upload data from the stream to your bucket.
    for line in stream_generator:
        line_as_byte = json.dumps(line, ensure_ascii=False).encode("utf-8")
        writer.write(line_as_byte + b"\n")
    writer.close()

    # Rewind the stream to the beginning. This step can be omitted if the input
    # stream will always be at a correct position.
    # file_obj.seek(0)

    print(f"Stream data uploaded to {destination_blob_name} in bucket {bucket_name}.")


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
