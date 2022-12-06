"""
Script to extract Named Entities from GOV.UK pages using a trained Spacy NER pipeline model.

The script saves the extracted entities to a number of .jsonl files, to the local disk.

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
import torch
import json
from typing import Generator
from google.cloud import bigquery, storage
import tqdm
import GPUtil
from thinc.api import get_current_ops, set_gpu_allocator

# For GPU memory allocation management
# https://github.com/explosion/spaCy/issues/9432
set_gpu_allocator("pytorch")

# Check if Spacy can see/use GPU
is_using_gpu = spacy.prefer_gpu()
if is_using_gpu:
    print("Using GPU!")
    spacy.require_gpu()
    print("GPU Usage")
    GPUtil.showUtilization()
else:
    print("GPU not found.")

print(f"get_current_ops: {get_current_ops()}")


def make_inference(rows, ner_model, b, n, part_of_page, outfile):
    """
    Main function to extract named entities from a sequence of (text, (metadata)).

    Args:
        rows: a sequence of (text, context) tuples the form ("this is text", ("gov.uk/path", 1)),
            the output of the stream_rows_from_bigquery() function.
        ner_model: a Spacy NER model
        b: number of texts to buffer
        n: number of processors to use (default, 1)
        part_of_page: part of page from which to extract entities, one of 'title', 'text', 'description'
        outfile: filepath of the output JSONL file

    Returns:
        None
        Writes the extracted entities to a JSONL file.
    """
    results = extract_entities_pipe_from_tuples_to_dict(
        rows=rows, ner_model=ner_model, b=b, n=n, part_of_page=part_of_page
    )
    write_output_from_stream(outfile, results)


def stream_rows_from_bigquery(
    query: str,
    client: bigquery.client.Client,
    part_of_page: str,
):
    """
    Streams rows from a BigQuery table that contain rows of texts and metadata, into a generator.
    """
    query_job = client.query(query)
    if part_of_page == "text":
        for row in query_job:
            yield (row.get("line"), (row.get("url"), row.get("line_number")))
    elif part_of_page == "title":
        for row in query_job:
            yield (row.get("title"), (row.get("url")))
    elif part_of_page == "description":
        for row in query_job:
            yield (row.get("description"), (row.get("url")))


def extract_entities_pipe_from_tuples_to_dict(rows, ner_model, b, n, part_of_page: str):

    """
    Applies a trained Spacy NER pipeline model to a batch of texts as a stream,
    and yields the extracted named entities for each text in order as a generator.
    It calls the Spacy Language.pipe method (https://spacy.io/api/language#pipe).

    Args:
        rows: a sequence of (text, context) tuples the form ("this is text", ("gov.uk/path", 1)),
            the output of the stream_rows_from_bigquery() function.
        ner_model: a Spacy NER model
        b: number of texts to buffer
        n: number of processors to use (default, 1)
        part_of_page: part of page from which to extract entities, one of 'title', 'text', 'description'

    Returns:
        A generator yielding {"url": "gov.uk/path",
                            "entities: [(entity text, entity label, entity start, entity end)],
                            (), ...], "line_number: int} dictionaries.

    Notes: torch.no_grad() used for addressing GPU memery allocation at inference
    ref: https://github.com/explosion/spaCy/issues/9432
    https://stackoverflow.com/questions/69301276/spacy-inference-goes-oom-when-processing-several-documents
    https://pytorch.org/docs/stable/generated/torch.no_grad.html

    """

    if part_of_page == "text":
        with torch.no_grad():
            for doc, meta in tqdm.tqdm(
                ner_model.pipe(rows, as_tuples=True, batch_size=b, n_process=n)
            ):
                yield {
                    "url": meta[0],
                    "entities": [
                        {
                            "name": ent.text,
                            "type": ent.label_,
                            "start": ent.start_char,
                            "end": ent.end_char,
                        }
                        for ent in doc.ents
                    ],
                    "line_number": meta[1],
                }
    else:
        with torch.no_grad():
            for doc, meta in tqdm.tqdm(
                ner_model.pipe(rows, as_tuples=True, batch_size=b, n_process=n)
            ):
                yield {
                    "url": meta,
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


def write_output_from_stream(outfile: str, content_stream: Generator):
    """
    Writes outputs from a generator to JSONL format.

    NOTE: JSON does not preserve tuples and turn them into lists
    https://stackoverflow.com/questions/15721363/preserve-python-tuples-with-json
    """
    with open(outfile, "w") as f:
        for row in content_stream:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_model(path_to_model: str):
    # For GPU memory management during spacy.pipe inference
    # See https://spacy.io/api/pipeline-functions#doc_cleaner
    config = {"attrs": {"tensor": None}}
    nlp_model = spacy.load(path_to_model)
    nlp_model.add_pipe("doc_cleaner", config=config)
    print(f"Loaded model components:  {nlp_model.pipeline}")
    return nlp_model


if __name__ == "__main__":  # noqa: C901

    import argparse
    import yaml
    import time
    from datetime import date

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
    BQ_CLIENT = bigquery.Client(project=config["gcp_metadata"]["project_id"])
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
    SQL_QUERY = f"SELECT * FROM `{config['gcp_metadata']['project_id']}.{config['gcp_metadata']['bq_content_dataset']}.{PART_OF_PAGE}` LIMIT 40000"

    print("loading model...")
    nlp = load_model(MODEL_PATH)
    print(f"Model loaded successfully! Components: {nlp.pipe_names}")

    print("querying BigQuery for input...")
    content_stream = stream_rows_from_bigquery(
        query=SQL_QUERY, client=BQ_CLIENT, part_of_page=PART_OF_PAGE
    )

    print(f"starting extracting entities from {PART_OF_PAGE}...")
    OUTPUT_FILENAME = f"entities_{TARGET_DATE}_{PART_OF_PAGE}.jsonl"

    start = time.time()
    make_inference(
        rows=content_stream,
        ner_model=nlp,
        b=BATCH_SIZE,
        n=N_PROC,
        part_of_page=PART_OF_PAGE,
        outfile=OUTPUT_FILENAME,
    )
    print(time.time() - start)
