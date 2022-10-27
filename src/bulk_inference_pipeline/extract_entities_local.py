"""
Script to extract Named Entities from GOV.UK pages using a trained Spacy NER pipeline model,
on a local MacOS machine.

The script saves the extracted entities to a number of .jsonl files, to the `data/processed/entities` folder.

The entities are extracted separately from titles, descriptions and texts, based on the user's input.

For each "part of page" (title, description, text), the number of saved files depends on the chosen `chunk_size` value and
the total number of texts to be processed.

File names follow the schema: "entities_{DATE}_{PART_OF_PAGE}_{CHUNK_INDEX}.jsonl",
for instance "entities_200722_title_1.jsonl".

Requirements:
- A copy of the preprocessed content store - see `src/make_data/get_preproc_content.py`
- A trained Spacy NER model
- Patience...

Nice to have:
- An Apple M1 Pro processor, with the https://github.com/explosion/thinc-apple-ops module installed.
    This will make inference faster by exploting Apple's native libraries for
    matrix multiplication (see https://github.com/explosion/thinc-apple-ops#prediction).

To optimise memory usage (so your laptop does not crash) and processing time, the script does:
- sequentially stream texts to the pipeline in chunks of specified `chunk_size`, releasing memory
    after the execution of each chunk, thus avoiding RAM overload;
- support sequential batch processing for NER inference, with specified `batch_size`;
- support parallel processing, if `n_process` is set > 1.
The content store is never loaded wholly into memory.

See below for more details.

The script takes the following arguments:

- "--ner_model", "-m":
        Full path to NER model to use for inference.

- "--part_of_page", "-p":
        Part of page from which to extract entities, one of 'title', 'description', 'text'.

- "--chunk_size", "-c" [OPTIONAL, default is 40,000]:
        Chunk size; number of texts to be streamed before memory is released.
        The ideal value depends on the total number and length of texts being processed.
        Example. The preprocessed content store contains something between 500,000 and 650,000 texts.
        Setting a chunk_size of 40,000 would mean processing e.g. 600,000/40,000 = 15 chunks.

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

a) with default values for the optional arguments
```
python src/bulk_inference_pipeline/extract_entities_local.py \
    -p "title" -m "models/mdl_ner_trf_b1_b4/model-best"
```

b) with user-defined values for the optional arguments (recommended)
```
python src/bulk_inference_pipeline/extract_entities_local.py \
    -p "title" \
        -m "models/mdl_ner_trf_b1_b4/model-best" \
                --chunk_size 10000 \
                    --batch_size 6000 \
                        --n_proc 5
```

Additional Notes:

- The current pipeline extracts entities from Title and Description of ** all ** the GOV.UK pages
    in the preprocessed content store; but it only extract entities from the body Text of a subset of
    GOV.UK pages, those with the specified document_type or publishing_app.
    This still amounts for 30-40% of all pages on GOV.UK. We hope to remove this caveat once the
    pipeline is moved to the cloud and we have fewer memory and processing constraints.

- Finding a suitable compromise between "--batch_size" and "n_proc".
    `batch_size` determines the size of each batch of texts being worked on by each process.
    If the `batch_size` value is too small, then a large number of workers (as available given
    your CPU cores and your set value for `n_proc` when > 1) will spin up to deal with the large number
    of batches overall. This can slow down execution.
    Yet, sometimes you want `batch_size` to be relatively small when the length of the texts being process is long.
    See "--batch_size", "-b" above for more info.

- Choosing suitable values for "--chunk_size", "--batch_size" and "n_proc" requires some thinking and iterations.
    What has worked when training on a M1 Pro processor, but could potentially be improved further
    by experimenting on values:
    - Title (very short texts): --chunk_size 40000 --batch_size 6000 --n_proc 8
    - Description (short texts): --chunk_size 20000 --batch_size 6000 --n_proc 8
    - Text (long/very-long texts): --chunk_size 15000 --batch_size 30 --n_proc 5

"""

import time

import spacy

from typing import Generator, Dict, Tuple
from google.cloud import bigquery, storage

from src.infer_entities.utils import upload_jsonl_from_stream


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


def extract_entities_pipe(
    texts: Tuple[str, Dict[str, str]],
    ner_model: spacy.Language,
    part_of_page: str,
    batch_size=5000,
    n_process=1,
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
        texts, as_tuples=True, batch_size=batch_size, n_process=n_process
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


def make_inference_from_stream(
    rows: Generator[dict[str, str], None, None],
    part_of_page: str,
    ner_model: spacy.Language,
    storage_client,
    bucket_name,
    destination_blob_name,
    batch_size: int,
    n_process: int = 1,
):
    """
    Main function to extract named entities from a sequence of {text, context}.
    """

    tuple_rows = to_tuples_from_stream(rows=rows, part_of_page=part_of_page)

    entities_rows = extract_entities_pipe(
        texts=tuple_rows,
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


if __name__ == "__main__":  # noqa: C901

    import argparse
    import yaml
    from datetime import date, timedelta
    from src.infer_entities.utils import load_model, chunks, stream_from_bigquery

    with open("src/bulk_inference_pipeline/bulk_inference_config.yml", "r") as file:
        config = yaml.safe_load(file)

    parser = argparse.ArgumentParser(
        description="Run src.bulk_inference_pipeline.infer_entities_local"
    )

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
        required=True,
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
        "-c",
        "--chunk_size",
        type=int,
        action="store",
        required=False,
        default=40000,
        help="Specify the chunk size; default is 40000.",
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
        yesterday = today - timedelta(days=1)
        TARGET_DATE = yesterday.strftime("%d%m%y")

    MODEL_PATH = parsed_args.ner_model
    PART_OF_PAGE = parsed_args.part_of_page
    CHUNK_SIZE = parsed_args.chunk_size
    BATCH_SIZE = parsed_args.batch_size
    N_PROC = parsed_args.n_proc

    # TODO: move to function?
    SQL_QUERY = f"SELECT * FROM `{config['gcp_metadata']['project_id']}.{config['gcp_metadata']['bq_content_dataset']}.{PART_OF_PAGE}`"

    print("Loading model...")
    nlp = load_model(MODEL_PATH)
    # add rule-based component (faster) to split text into sentences
    # nlp.add_pipe("sentencizer", first=True)
    print(f"Model loaded successfully! Components: {nlp.pipe_names}")

    print("Querying BigQuery...")
    content_stream = stream_from_bigquery(query=SQL_QUERY, client=BQ_CLIENT)
    print("Done.")

    print(f"starting inference on {PART_OF_PAGE}...")

    for i, chunk_stream in enumerate(chunks(content_stream, CHUNK_SIZE)):

        print(f"{PART_OF_PAGE}: {i}")
        start = time.time()
        try:

            OUTPUT_FILENAME = f"entities_{TARGET_DATE}_{PART_OF_PAGE}_{i}.jsonl"
            make_inference_from_stream(
                rows=chunk_stream,
                part_of_page=PART_OF_PAGE,
                ner_model=nlp,
                batch_size=BATCH_SIZE,
                n_process=N_PROC,
                storage_client=STORAGE_CLIENT,
                bucket_name="cpto-content-metadata",
                destination_blob_name="content_ner/" + OUTPUT_FILENAME,
            )

        except AttributeError as e:
            print(e)
            pass

        print(time.time() - start)
