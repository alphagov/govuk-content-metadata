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

Example, to extract entities from the titles of all the pages in the
2022-07-20 copy of the preprocessed content store using a trained NER model saved in the "models/"
folder, from the root directory you can run:

a) with default values for the optional arguments
```
python src/bulk_inference_pipeline/extract_entities_cloud.py -p "title" -m "models/mdl_ner_trf_b1_b4/model-best"
```
"""

import time

import spacy

from typing import Generator
from google.cloud import bigquery, storage

from utils import upload_jsonl_from_stream


def extract_entities(rows, part_of_page: str, ner_model):
    """
    Applies a trained Spacy NER pipeline model to a stream of texts,
    and yields the extracted named entities for each text in order.

    Args:
        rows:
        ner_model: a Spacy NER model

    Returns:
        A generator yielding {"url": "gov.uk/path", "entities: [{"name": "entity_name",
                                "type": "entity_label", "start": entity_start_char,
                                "end": entity_end_char}, {...}, ...], "line_number": int}
                                dictionaries.
    """

    valid_part_of_page = {"text", "title", "description"}
    while part_of_page not in valid_part_of_page:
        raise ValueError(f"part_of_page must be one of {valid_part_of_page}.")
    try:
        if part_of_page == "text":
            for row in rows:
                doc = ner_model(row.get("line"))
                yield {
                    "url": row.get("url"),
                    "entities": [
                        {
                            "name": ent.text,
                            "type": ent.label_,
                            "start": ent.start_char,
                            "end": ent.end_char,
                        }
                        for ent in doc.ents
                    ],
                    "line_number": row.get("line_number"),
                }
        else:  # title / description
            for row in rows:
                doc = nlp(row.get(part_of_page))
                yield {
                    "url": row.get("url"),
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
    except Exception as e:
        return e


def make_inference_from_stream(
    rows: Generator[dict[str, str], None, None],
    part_of_page: str,
    ner_model: spacy.Language,
    storage_client,
    bucket_name,
    destination_blob_name,
):
    """
    Main function to extract named entities from a sequence of {text, context}.
    """

    entities_rows = extract_entities(
        rows=rows,
        part_of_page=part_of_page,
        ner_model=ner_model,
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
    from datetime import date
    from utils import load_model, stream_from_bigquery

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

    # TODO: move to function?
    SQL_QUERY = f"SELECT * FROM `{config['gcp_metadata']['project_id']}.{config['gcp_metadata']['bq_content_dataset']}.{PART_OF_PAGE}`"

    print("Loading model...")
    nlp = load_model(MODEL_PATH)
    print(f"Model loaded successfully! Components: {nlp.pipe_names}")

    print("Querying BigQuery...")
    content_stream = stream_from_bigquery(query=SQL_QUERY, client=BQ_CLIENT)
    print("Done.")

    print(f"starting inference on {PART_OF_PAGE}...")
    OUTPUT_FILENAME = f"entities_{TARGET_DATE}_{PART_OF_PAGE}.jsonl"

    start = time.time()

    make_inference_from_stream(
        rows=content_stream,
        part_of_page=PART_OF_PAGE,
        ner_model=nlp,
        storage_client=STORAGE_CLIENT,
        bucket_name="cpto-content-metadata",
        destination_blob_name="content_ner/" + OUTPUT_FILENAME,
    )
