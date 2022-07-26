import gzip
import csv
import json

# import profile

from itertools import islice

# from memory_profiler import profile
import time
from typing import Iterator, Dict, Tuple
import spacy

import sys

# import multiprocessing

MODEL_PATH = "models/mdl_ner_trf_b1_b4/model-best"
# print("Loading model...")
# start = time.time()
# nlp = spacy.load(MODEL_PATH)
# print("Model loaded successfully")
# print(time.time() - start)
# add rule-based component (faster) to split text into sentences
# nlp.add_pipe("sentencizer", first=True)
# nlp.pipe_names


KEEP_FIELDS = [
    "base_path",
    "title",
    "description",
    "text",
]

KEEP_PUBISIHING_APPS = ["publisher", "contact", "travel_advice_publisher"]
KEEP_DOCUMENT_TYPES = [
    "detailed_guide",
    "detailed_guidance",
    "government_response",
    "news_story",
    "press_release",
    "organisation",
    "person",
    "decision",
    "form",
    "guidance",
    "international_treaty",
    "notice",
    "policy_paper",
    "regulation",
    "statuatory_guidance",
    "transparency",
    "ministerial_role",
    "speech",
    "working_group",
    "take_part",
]


def load_model(path_to_model: str = MODEL_PATH):
    return spacy.load(path_to_model)


def source_gen(
    n: int,
    filename: str,
    delimiter="\t",
    encoding="utf-8",
    quoting=csv.QUOTE_MINIMAL,
    skipinitialspace=True,
    fields_to_keep=KEEP_FIELDS,
    doctypes_to_keep=None,
    pubapp_to_keep=None,
):
    # A data source that will yield N values.
    with gzip.open(filename, "rt", encoding) as f:
        reader = csv.DictReader(
            f, delimiter=delimiter, skipinitialspace=skipinitialspace, quoting=quoting
        )

        for i, row in enumerate(reader):
            if (row["publishing_app"] in set(pubapp_to_keep)) or (
                row["document_type"] in set(doctypes_to_keep)
            ):
                yield {k: v for k, v in row.items() if k in fields_to_keep}
            else:
                pass
            if i >= n:
                break


def chunks(iterable, size=10):
    """
    https://python.tutorialink.com/split-a-generator-into-chunks-without-pre-walking-it/
    """
    # iterator = iter(iterable)
    for first in iterable:  # stops when iterator is depleted

        def chunk():  # construct generator for next chunk
            yield first  # yield element from for loop
            for more in islice(iterable, size - 1):
                yield more  # yield more elements from the iterator

        yield chunk()  # in outer generator, yield next chunk


def gzipped_csv_to_stream(
    filename: str,
    delimiter="\t",
    encoding="utf-8",
    quoting=csv.QUOTE_MINIMAL,
    skipinitialspace=True,
    fields_to_keep=KEEP_FIELDS,
) -> Iterator[Dict[str, str]]:
    with gzip.open(filename, "rt", encoding) as f:
        reader = csv.DictReader(
            f, delimiter=delimiter, skipinitialspace=skipinitialspace, quoting=quoting
        )
        for row in reader:
            yield {k: v for k, v in row.items() if k in fields_to_keep and ()}


def to_tuples(
    lines: Iterator[Dict[str, str]], key_with_text: str, key_id: str = "base_path"
):
    for line in lines:
        try:
            yield (
                line[key_with_text] if line[key_with_text] is not None else "",
                {key_id: line.get(key_id, "unknown")},
            )
        # handle empty {} originiated by filtering for doc types / pub apps
        except KeyError:
            continue


def extract_entities(
    texts: Tuple[str, Dict[str, str]], ner_model, batch_size=5000, n_process=1
):
    for doc, meta in ner_model.pipe(
        texts, as_tuples=True, batch_size=batch_size, n_process=n_process
    ):
        yield {
            meta["base_path"]: [
                (ent.text, ent.label_, ent.start_char, ent.end_char) for ent in doc.ents
            ]
        }


def make_inference(
    content_stream,
    position,
    ner_model,
    batch_size,
    output_file,
    key_id="base_path",
    n_process=1,
):

    tuple_content_stream = to_tuples(content_stream, position, key_id)
    results_entities = extract_entities(
        tuple_content_stream,
        ner_model=ner_model,
        batch_size=batch_size,
        n_process=n_process,
    )
    write_output(output_file, results_entities)


def write_output(outfile, content_strem):
    """
    NOTE: JSON does not preserve tuples and turn them into lists
    https://stackoverflow.com/questions/15721363/preserve-python-tuples-with-json
    """
    with open(outfile, "w") as f:
        for row in content_strem:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    # import sys

    OUTPUT_FOLDER = "data/processed/entities/"
    DATE_SHORT = "200722"
    INPUT_CONTENT = f"data/raw/preprocessed_content_store_{DATE_SHORT}.csv.gz"
    # POSITION = "description"
    POSITION = "text"
    MAX = 700000
    CHUNK_SIZE = int(MAX / 46) + 2
    BATCH_SIZE = 30
    N_PROC = 6

    # Allow the largest field size possible.
    # from https://stackoverflow.com/a/15063941
    maxInt = sys.maxsize
    while True:
        # decrease the maxInt value by factor 10
        # as long as the OverflowError occurs.
        try:
            csv.field_size_limit(maxInt)
            break
        except OverflowError:
            maxInt = int(maxInt / 10)
    csv.field_size_limit(maxInt)

    print("Loading model...")
    nlp = load_model(MODEL_PATH)
    # add rule-based component (faster) to split text into sentences
    nlp.add_pipe("sentencizer", first=True)
    print(f"Model loaded successfully! Components: {nlp.pipe_names}")

    if POSITION == "text":
        content_stream = source_gen(
            n=MAX,
            filename=INPUT_CONTENT,
            pubapp_to_keep=KEEP_PUBISIHING_APPS,
            doctypes_to_keep=KEEP_DOCUMENT_TYPES,
        )
    else:
        content_stream = gzipped_csv_to_stream(INPUT_CONTENT)
    # content_stream = source_gen(n=MAX, filename=INPUT_CONTENT)

    print(f"starting inference on {POSITION}...")

    for i, chunk_stream in enumerate(chunks(content_stream, CHUNK_SIZE)):

        print(f"{POSITION}: {i}")
        start = time.time()
        try:

            OUTPUT_FILENAME = f"entities_{DATE_SHORT}_{POSITION}_{i}.jsonl"
            OUTPUT_FILEPATH = OUTPUT_FOLDER + OUTPUT_FILENAME
            make_inference(
                content_stream=chunk_stream,
                position=POSITION,
                ner_model=nlp,
                batch_size=BATCH_SIZE,
                key_id="base_path",
                n_process=N_PROC,
                output_file=OUTPUT_FILEPATH,
            )

        except AttributeError as e:
            print(e)
            pass

        print(time.time() - start)
