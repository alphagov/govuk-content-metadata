import pytest
import types
import gzip
from io import BytesIO
from unittest.mock import patch, mock_open, call

from bulk_inference_pipeline.src.utils import chunks, write_output_from_stream

from bulk_inference_pipeline.extract_entities_cloud import (
    to_tuples_from_stream,
    extract_entities_pipe,
)


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


args_to_tuples_correct = [
    (
        [
            {"title": "This is a title", "url": "base_path"},
            {"title": "This is a second title", "url": "base_path2"},
        ],
        "title",
        [
            ("This is a title", {"url": "base_path"}),
            ("This is a second title", {"url": "base_path2"}),
        ],
    ),
    (
        [
            {
                "line": "This is a line of text.",
                "url": "base_path",
                "line_number": 3,
            },
            {
                "line": "Here is another line text.",
                "url": "base_path2",
                "line_number": 1,
            },
        ],
        "text",
        [
            ("This is a line of text.", {"url": "base_path", "line_number": 3}),
            ("Here is another line text.", {"url": "base_path2", "line_number": 1}),
        ],
    ),
    (
        [
            {
                "title": "This is a title",
                "bla": "nonsense voila",
                "blu": 1234,
                "url": "unique_identifier/usually/base_path",
            }
        ],
        "title",
        [("This is a title", {"url": "unique_identifier/usually/base_path"})],
    ),
]


@pytest.mark.parametrize("test_input, arg1, test_expected", args_to_tuples_correct)
def test_to_tuples_expected(test_input: str, arg1: str, test_expected: str) -> None:
    """Assert to_tuples_from_stream() returns correctly."""
    assert list(to_tuples_from_stream(test_input, arg1)) == test_expected


def test_to_tuples_output_type():
    """Assert output of to_tuples_from_stream() is a generator"""
    input_generator = (
        x
        for x in [
            {"title": "This is a title", "url": "base_path"},
            {"title": "This is a second title", "url": "base_path2"},
        ]
    )
    output_generator = to_tuples_from_stream(input_generator, "title")
    assert isinstance(output_generator, types.GeneratorType)


args_to_tuples_handles_error = [
    ([{}, {}], "title", [("", {"url": None}), ("", {"url": None})]),
    ([{}], "title", [("", {"url": None})]),
    (
        [{}, {"title": "a", "url": 1}],
        "title",
        [(("", {"url": None})), ("a", {"url": 1})],
    ),
]


@pytest.mark.parametrize(
    "test_input, arg1, test_expected", args_to_tuples_handles_error
)
def test_to_tuples_handles_keyerror(
    test_input: str, arg1: str, test_expected: str
) -> None:
    """Test to_tuples_from_stream() handles a KeyError correctly."""
    assert list(to_tuples_from_stream(test_input, arg1)) == test_expected


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


def test_write_output_from_stream():
    input_generator = (x for x in [{"t": "abc"}, {"t": "def"}])
    expected = [call({"t": "abc"}), call({"t": "def"})]
    open_mock = mock_open()
    with patch("builtins.open", open_mock, create=True):
        write_output_from_stream("test_out.jsonl", input_generator)
    open_mock.assert_called_with("test_out.jsonl", "w")
    open_mock.call_args_list == expected


"""
texts: Tuple[str, Dict[str, str]],
   texts: Tuple[str, Dict[str, str]],
    ner_model: spacy.Language,
    part_of_page: str,
    batch_size: int,
    n_process: int,
"""

args_extract_entities_pipe_input1 = [
    ("The UK is an entity and so is Spain.", {"url": "abc/"}),
    ("Serena Williams is also an entity", {"url": "def/"}),
]
args_extract_entities_pipe_expected1 = [
    {
        "url": "abc/",
        "entities": [
            {"name": "UK", "type": "GPE", "start": 4, "end": 6},
            {"name": "Spain", "type": "GPE", "start": 30, "end": 35},
        ],
    },
    {
        "url": "def/",
        "entities": [
            {"name": "Serena Williams", "type": "PERSON", "start": 0, "end": 15}
        ],
    },
]
args_extract_entities_pipe_input2 = [
    ("Serena Williams is also an entity", {"url": "def/", "line_number": 1})
]
args_extract_entities_pipe_expected2 = [
    {
        "url": "def/",
        "entities": [
            {"name": "Serena Williams", "type": "PERSON", "start": 0, "end": 15}
        ],
        "line_number": 1,
    }
]


def test_extract_entities_output_type(en_core_web_lg):
    input_generator = (x for x in args_extract_entities_pipe_input1)
    output = extract_entities_pipe(
        input_generator, en_core_web_lg, "title", batch_size=1, n_process=1
    )
    assert isinstance(output, types.GeneratorType)


def test_extract_entities_output_structure1(en_core_web_lg):
    input_generator = (x for x in args_extract_entities_pipe_input1)
    output = extract_entities_pipe(
        input_generator, en_core_web_lg, "title", batch_size=1, n_process=1
    )
    output_element_1 = next(output)
    output_element_2 = next(output)
    assert isinstance(output_element_1, dict)
    assert [k in output_element_1.keys() for k in ["url", "entities"]]
    assert [k in output_element_2.keys() for k in ["url", "entities"]]
    assert [isinstance(v[0], str) for v in output_element_1.values()]
    assert [isinstance(v[1], list) for v in output_element_1.values()]
    assert [isinstance(d, dict) for v in output_element_1.values() for d in v]


def test_extract_entities_output_structure2(en_core_web_lg):
    input_generator = (x for x in args_extract_entities_pipe_input2)
    output = extract_entities_pipe(
        input_generator, en_core_web_lg, "text", batch_size=1, n_process=1
    )
    output_element_1 = next(output)
    assert isinstance(output_element_1, dict)
    assert [k in output_element_1.keys() for k in ["url", "entities", "line_number"]]
    assert [isinstance(v, str) for k, v in output_element_1.items() if k == "url"]
    assert [isinstance(v, list) for k, v in output_element_1.items() if k == "entities"]
    assert [
        isinstance(v[0], dict) for k, v in output_element_1.items() if k == "entities"
    ]
    assert [
        isinstance(v, int) for k, v in output_element_1.items() if k == "line_number"
    ]


def test_extract_entities_correct_title(en_core_web_lg):
    input_generator = (x for x in args_extract_entities_pipe_input1)
    output = extract_entities_pipe(
        input_generator, en_core_web_lg, "title", batch_size=1, n_process=1
    )
    assert list(output) == args_extract_entities_pipe_expected1


def test_extract_entities_correct_text(en_core_web_lg):
    input_generator = (x for x in args_extract_entities_pipe_input2)
    output = extract_entities_pipe(
        input_generator, en_core_web_lg, "text", batch_size=1, n_process=1
    )
    assert list(output) == args_extract_entities_pipe_expected2
