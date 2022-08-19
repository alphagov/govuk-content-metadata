import gzip
import csv
import json
import sys
import time

import spacy

from itertools import islice
from typing import Generator, Dict, Tuple, List


KEEP_FIELDS = [
    "base_path",
    "title",
    "description",
    "text",
]

KEEP_PUBLISIHING_APPS = ["publisher", "contact", "travel_advice_publisher"]
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


def load_model(path_to_model: str):
    return spacy.load(path_to_model)


def gzipped_csv_to_stream(
    filename: str, fields_to_keep: List[str] = None, encoding: str = "utf-8", **kwargs
) -> Generator[Dict[str, str], None, None]:
    """
    Sources a gzipped csv file, filtering for the specified fields if provided.
    Returns a generator.

    Args:
        fileneme: full path name of the gzipped csv file
        fields_to_keep [optional]: list of names of fields to keep
        encoding: encoding of the file (default: 'utf-8')
        **kwargs: parameters passed to the csv.DictReader function. See ?csv.DictReader for more info.

    Returns:
        A generator yielding rows of the original gzipped csv file.
    """
    with gzip.open(filename, "rt", encoding) as f:
        reader = csv.DictReader(f, **kwargs)
        for row in reader:
            if fields_to_keep:
                yield {k: v for k, v in row.items() if k in fields_to_keep}
            yield {k: v for k, v in row.items()}


def source_filter_content_gen(
    n: int,
    filename: str,
    encoding="utf-8",
    fields_to_keep: List[str] = None,
    doctypes_to_keep: List[str] = None,
    pubapps_to_keep: List[str] = None,
    **kwargs,
):
    """
    Sources the preprocessed content store gzipped csv file as a generator of `n` elements.
    It filters for the specified document_types and publishing_apps, and [optional] only returns
    the selected fields.
    This is useful if you do not need/want to source the whole content store.

    #TODO: admittingly, not a very elegant general solution, but wanted to avoid too many `if... else...`

    Args:
        n: number of rows to source from the gzipped csv file
        fileneme: full path name of the gzipped csv file
        encoding: encoding of the file (default: 'utf-8')
        fields_to_keep [optional]: list of names of fields to keep
        doctypes_to_keep: list of document_types to keep
        pubapps_to_keep: list of publishing_apps to keep
        **kwargs: parameters passed to the csv.DictReader function. See ?csv.DictReader for more info.

    Returns:
        A generator yielding rows of the original gzipped csv file.
    """
    # A data source that will yield N values.
    with gzip.open(filename, "rt", encoding) as f:
        reader = csv.DictReader(f, **kwargs)

        for i, row in enumerate(reader):
            if (row["publishing_app"] in set(pubapps_to_keep)) or (
                row["document_type"] in set(doctypes_to_keep)
            ):
                if fields_to_keep:
                    yield {k: v for k, v in row.items() if k in fields_to_keep}
                yield {k: v for k, v in row.items()}
            else:
                pass
            if i >= n:
                break


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


def to_tuples(
    lines: Generator[dict[str, str], None, None],
    key_with_text: str,
    key_id: str,
):
    """
    Formats the elements of a generator, each being a dictionary containing the `key_with_text` and `key_id` keys,
    into a generator of tuples of the form (<key_with_text>, {`key_id`: <key_id>}).
    This is the format required for NER inference by the Spacy framework.

    Example:
        from
        {"title": "This is a title", "id": "unique_identifier/usually/base_path"}
        to
        ("This is a title", {"id": "unique_identifier/usually/base_path"})

    Args:
        lines: generator yielding dictionaries containing content
        key_with_text: name of the dictionary key containing text (e.g., "title")
        key_id: name of the dictionary key uniquely identifying each generator element (e.g., "base_path")

    Returns:
        A generator of the reformatted content yiedling tuples (text, "key_id": id_value).
    """

    for line in lines:
        try:
            yield (
                line[key_with_text] if line[key_with_text] is not None else "",
                {key_id: line.get(key_id, "unknown")},
            )
        # handle empty {} originated by filtering for doc types / pub apps
        except KeyError:
            continue


def extract_entities(
    texts: Tuple[str, Dict[str, str]],
    ner_model: spacy.Language,
    id_key: str,
    batch_size=5000,
    n_process=1,
):
    """

    Applies a trained Spacy NER pipeline model to a batch of texts as a stream,
    and yields the extracted named entities for each text in order.
    It calls the Spacy Language.pipe method (https://spacy.io/api/language#pipe).

    Args:
        texts: a sequence of (text, context) tuples the form ("this is text", {id_key: "unique_id"}),
            the output of the to_tuples() function.
        id_key: a text's unique identifier (usually, "base_path")
        ner_model: a Spacy NER model
        batch_size: number of texts to buffer.
        n_process: number of processors to use (default, 1).

    Returns:
        A generator yielding {"unique_id", [(entity text, entity label, entity start, entity end)], (), ...} dictionaries.
    """
    for doc, meta in ner_model.pipe(
        texts, as_tuples=True, batch_size=batch_size, n_process=n_process
    ):
        yield {
            meta[id_key]: [
                (ent.text, ent.label_, ent.start_char, ent.end_char) for ent in doc.ents
            ]
        }


def make_inference(
    content_stream: Generator[dict[str, str], None, None],
    position: str,
    ner_model: spacy.Language,
    batch_size: int,
    output_file: str,
    key_id: str = "base_path",
    n_process: int = 1,
):
    """
    Main function to extract named entities from a sequence of {text, context}.
    """

    tuple_content_stream = to_tuples(
        lines=content_stream, key_with_text=position, key_id=key_id
    )
    results_entities = extract_entities(
        texts=tuple_content_stream,
        ner_model=ner_model,
        id_key=key_id,
        batch_size=batch_size,
        n_process=n_process,
    )
    write_output(output_file, results_entities)


def write_output(outfile: str, content_stream: Generator):
    """
    Writes outputs from a generator to JSONL format.

    NOTE: JSON does not preserve tuples and turn them into lists
    https://stackoverflow.com/questions/15721363/preserve-python-tuples-with-json
    """
    with open(outfile, "w") as f:
        for row in content_stream:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


if __name__ == "__main__":  # noqa: C901

    import argparse
    from datetime import date, timedelta
    from src.utils.helpers_formatting import shorten_date_format

    parser = argparse.ArgumentParser(description="Run src.make_data.infer_entities")

    parser.add_argument(
        "-m",
        "--ner_model",
        type=str,
        action="store",
        required=True,
        # default="models/mdl_ner_trf_b1_b4/model-best"
        help="Full path to NER model to use for inference.",
    )

    parser.add_argument(
        "-p",
        "--part_of_page",
        type=str,
        action="store",
        required=True,
        choices=["title", "description", "text"],
        default="title",
        help="Specify: 'title', 'description' or 'text'.",
    )

    parser.add_argument(
        "-d",
        "--date",
        type=str,
        action="store",
        dest="date",
        required=False,
        help="Specify the date 'YYYY-MM-DD' of the preprocessed content store copy; default is yesterday.",
    )

    parser.add_argument(
        "--max",
        type=int,
        required=False,
        default=700000,
        help="Set up upper limit for the number of content items that will be processes; default is 700,000.",
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

    # Default is yesterday unless a date is provided by the user
    if parsed_args.date:
        TARGET_DATE = parsed_args.date
    else:
        today = date.today()
        TARGET_DATE = today - timedelta(days=1)

    TARGET_DATE_SHORT = shorten_date_format(TARGET_DATE)

    OUTPUT_FOLDER = "data/processed/entities/"
    INPUT_CONTENT = f"data/raw/preprocessed_content_store_{TARGET_DATE_SHORT}.csv.gz"

    POSITION = parsed_args.part_of_page
    MAX = parsed_args.max
    CHUNK_SIZE = int(MAX / 46) + 2
    BATCH_SIZE = parsed_args.batch_size
    N_PROC = parsed_args.n_proc
    MODEL_PATH = parsed_args.ner_model

    # Address issue with csv fields containing lots of text
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
        content_stream = source_filter_content_gen(
            n=MAX,
            filename=INPUT_CONTENT,
            fields_to_keep=KEEP_FIELDS,
            pubapps_to_keep=KEEP_PUBLISIHING_APPS,
            doctypes_to_keep=KEEP_DOCUMENT_TYPES,
            delimiter="\t",
            quoting=csv.QUOTE_MINIMAL,
            skipinitialspace=True,
        )
    else:
        content_stream = gzipped_csv_to_stream(
            filename=INPUT_CONTENT,
            fields_to_keep=KEEP_FIELDS,
            delimiter="\t",
            quoting=csv.QUOTE_MINIMAL,
            skipinitialspace=True,
        )

    print(f"starting inference on {POSITION}...")

    for i, chunk_stream in enumerate(chunks(content_stream, CHUNK_SIZE)):

        print(f"{POSITION}: {i}")
        start = time.time()
        try:

            OUTPUT_FILENAME = f"JUNK_entities_{TARGET_DATE_SHORT}_{POSITION}_{i}.jsonl"
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
