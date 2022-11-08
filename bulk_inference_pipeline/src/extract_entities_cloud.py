"""
Script to extract Named Entities from GOV.UK pages using a trained Spacy NER pipeline model.

The script saves the extracted entities to a number of .jsonl files, to the Project's Google Storage.

The entities are extracted separately from titles, descriptions and texts, based on the user's input.

Requirements:
- GCP access
- A trained Spacy NER model
- Patience...

The script takes the following arguments:

- "--ner_model", "-m":
        Full path to NER model to use for inference.

- "--part_of_page", "-p":
        Part of page from which to extract entities, one of 'title', 'description', 'text'.

- "--batch_size", "-b" [OPTIONAL, default is 30]:
        Batch size; number of texts to be batched processed by the Spacy pipeline.
        The ideal value depends on the texts being processed, in particular how long they are.
        For reasonably long-sized text such as news articles or guidances,
        it makes sense to keep the batch size reasonably small
        (so that each batch doesn't contain really long texts); for instance, 20 or 30.
        For shorter texts (e.g. titles, descriptions) where each document is much shorter in length,
        a larger batch size can be used; for instance, between 5,000-10,000.
        For more suggestions, see:
        https://prrao87.github.io/blog/spacy/nlp/performance/2020/05/02/\
            spacy-multiprocess.html#Option-1:-Sequentially-process-DataFrame-column


- "--n_proc", "-n" [OPTIONAL, default is 1]:
        Number of cores for the parallel processing of texts.
        Note that multiprocessing has a lot of overhead when starting child processes,
        thus the choice of value may require to carefully consider both
        the chosen `batch_size` value and the overall number of texts to be processed.

Example, to extract entities from the titles of all the pages in the
2022-07-20 copy of the preprocessed content store using a trained NER model saved in the "models/"
folder, from the root directory you can run:

```
python src/bulk_inference_pipeline/extract_entities_cloud.py \
    -p "title" \
        -m "models/mdl_ner_trf_b1_b4/model-best" \
            --batch_size 6000 \
                        --n_proc 5
```

Notes:

- Finding a suitable compromise between "--batch_size" and "n_proc".
    `batch_size` determines the size of each batch of texts being worked on by each process.
    If the `batch_size` value is too small, then a large number of workers (as available given
    your CPU cores and your set value for `n_proc` when > 1) will spin up to deal with the large number
    of batches overall. This can slow down execution.
    Yet, sometimes you want `batch_size` to be relatively small when the length of the texts being process is long.
    See "--batch_size", "-b" above for more info.

"""

import spacy
import json
from typing import Generator, Dict, Tuple
from google.cloud import bigquery, storage
from google.cloud.storage.fileio import BlobWriter


def make_inference_from_stream(
    rows: Generator[dict[str, str], None, None],
    part_of_page: str,
    ner_model: spacy.Language,
    storage_client,
    bucket_name,
    destination_blob_name,
    batch_size: int,
    n_process: int,
):
    """
    Main function to extract named entities from a sequence of {text, context}.
    """

    tuple_rows = to_tuples_from_stream(rows=rows, part_of_page=part_of_page)

    entities_rows = extract_entities_pipe(
        rows=tuple_rows,
        part_of_page=part_of_page,
        ner_model=ner_model,
        batch_size=batch_size,
        n_process=n_process,
    )

    upload_jsonl_from_stream(
        storage_client=storage_client,
        bucket_name=bucket_name,
        stream_generator=entities_rows,
        destination_blob_name=destination_blob_name,
    )


def extract_entities_pipe(
    rows: Tuple[str, Dict[str, str]],
    ner_model: spacy.Language,
    part_of_page: str,
    batch_size: int,
    n_process: int,
):
    """

    Applies a trained Spacy NER pipeline model to a batch of texts as a stream,
    and yields the extracted named entities for each text in order.
    It calls the Spacy Language.pipe method (https://spacy.io/api/language#pipe).

    Args:
        texts: a sequence of (text, context) tuples the form ("this is text", {"url": "gov.uk/path", ...}),
            the output of the to_tuples_from_stream() function.
        ner_model: a Spacy NER model
        batch_size: number of texts to buffer.
        n_process: number of processors to use (default, 1).

    Returns:
        A generator yielding {"url": "gov.uk/path",
                            "entities: [(entity text, entity label, entity start, entity end)],
                            (), ...], "line_number: int} dictionaries.
    """
    for doc, meta in ner_model.pipe(
        rows, as_tuples=True, batch_size=batch_size, n_process=n_process
    ):
        if part_of_page == "text":
            yield {
                "url": meta["url"],
                "entities": [
                    {
                        "name": ent.text,
                        "type": ent.label_,
                        "start": ent.start_char,
                        "end": ent.end_char,
                    }
                    for ent in doc.ents
                ],
                "line_number": meta["line_number"],
            }
        else:  # title / description
            yield {
                "url": meta["url"],
                "entities": [
                    {
                        "name": ent.text,
                        "type": ent.label_,
                        "start": ent.start_char,
                        "end": ent.end_char,
                    }
                    for ent in doc.ents
                ],
            }


def to_tuples_from_stream(
    rows: Generator[bigquery.table.Row, None, None],
    part_of_page: str,
):
    """
    Formats the elements of a generator, each being a bigquery.table.Row with the following
    fields: "url" (all), "title" (if part_of_page is title), "description" (if part_of_page
    is description), "line" and "line_number" (if part_of_page is text),
    into a generator of tuples of the form (string of text, {"url": <url>, ...}).
    This is the format required for NER pipe inference by the Spacy framework.

    Example 1 (title):
        from
        {"title": "This is a title", "url": "gov.uk/base_path"}
        to
        ("This is a title", {"url": "gov.uk/base_path"})

    Example 2 (text):
        from
        {"line": "This is a line", "url": "gov.uk/base_path", "line_number": 3}
        to
        ("This is a line", {"url": "gov.uk/base_path", "line_number": 3})

    Args:
        rows: generator yielding dictionaries containing content
        part_of_page: one of "title", "description", "text"

    Returns:
        A generator of the reformatted content yiedling tuples (string of text, {"url": url, ...}).
    """

    if part_of_page == "text":
        for row in rows:
            yield (
                row.get("line") if row.get("line") is not None else "",
                {"url": row.get("url"), "line_number": row.get("line_number")},
            )
    else:
        for row in rows:
            yield (
                row.get(part_of_page) if row.get(part_of_page) is not None else "",
                {"url": row.get("url")},
            )


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


if __name__ == "__main__":  # noqa: C901

    import argparse
    import yaml
    from datetime import date
    from src.utils import load_model, stream_from_bigquery

    with open("bulk_inference_config.yml", "r") as file:
        config = yaml.safe_load(file)

    parser = argparse.ArgumentParser(description="Run extract_entities_cloud")

    parser.add_argument(
        "-m",
        "--ner_model",
        type=str,
        action="store",
        required=True,
        help="Full path to NER model to use for inference.",
    )

    parser.add_argument(
        "-d",
        "--date",
        type=str,
        action="store",
        dest="date",
        help="Date 'DDMMYY' of the data; default is yesterday.",
    )

    parser.add_argument(
        "-p",
        "--part_of_page",
        type=str,
        action="store",
        required=True,
        choices=["title", "description", "text"],
        help="Specify: 'title', 'description' or 'text'.",
    )

    parser.add_argument(
        "-b",
        "--batch_size",
        type=int,
        action="store",
        required=False,
        default=30,
        help="Specify the batch size; default is 30.",
    )

    parser.add_argument(
        "-n",
        "--n_proc",
        type=int,
        action="store",
        required=False,
        default=1,
        help="Specify the number of processes for parallel processing; default is 1.",
    )

    parsed_args = parser.parse_args()

    # Construct a BigQuery and a Gogle Stoarge client object.
    BQ_CLIENT = bigquery.Client()
    STORAGE_CLIENT = storage.Client()

    # Set date
    if parsed_args.date:
        TARGET_DATE = parsed_args.date
    else:
        today = date.today()
        TARGET_DATE = today.strftime("%d%m%y")

    MODEL_PATH = parsed_args.ner_model
    PART_OF_PAGE = parsed_args.part_of_page
    BATCH_SIZE = parsed_args.batch_size
    N_PROC = parsed_args.n_proc

    # TODO: move to function?
    SQL_QUERY = f"SELECT * FROM `{config['gcp_metadata']['project_id']}.{config['gcp_metadata']['bq_content_dataset']}.{PART_OF_PAGE}`"

    print("loading model...")
    nlp = load_model(MODEL_PATH)
    print(f"Model loaded successfully! Components: {nlp.pipe_names}")

    print("querying BigQuery for input...")
    content_stream = stream_from_bigquery(query=SQL_QUERY, client=BQ_CLIENT)

    print(f"starting extracting entities from {PART_OF_PAGE}...")
    OUTPUT_FILENAME = f"entities_{TARGET_DATE}_{PART_OF_PAGE}.jsonl"

    make_inference_from_stream(
        rows=content_stream,
        part_of_page=PART_OF_PAGE,
        ner_model=nlp,
        batch_size=BATCH_SIZE,
        n_process=N_PROC,
        storage_client=STORAGE_CLIENT,
        bucket_name="cpto-content-metadata",
        destination_blob_name="content_ner/" + OUTPUT_FILENAME,
    )
