import pytest
import types
import gzip
from io import BytesIO
from src.make_data.infer_entities import chunks, to_tuples, gzipped_csv_to_stream


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
            {"title": "This is a title", "id": "base_path"},
            {"title": "This is a second title", "id": "base_path2"},
        ],
        "title",
        "id",
        [
            ("This is a title", {"id": "base_path"}),
            ("This is a second title", {"id": "base_path2"}),
        ],
    ),
    (
        [
            {
                "title": "This is a title",
                "text": "This is some text.",
                "id": "base_path",
            },
            {
                "title": "This is a second title",
                "text": "Here is some more text.",
                "id": "base_path2",
            },
        ],
        "text",
        "id",
        [
            ("This is some text.", {"id": "base_path"}),
            ("Here is some more text.", {"id": "base_path2"}),
        ],
    ),
    (
        [
            {
                "title": "This is a title",
                "bla": "nonsense voila",
                "blu": 1234,
                "id": "unique_identifier/usually/base_path",
            }
        ],
        "title",
        "id",
        [("This is a title", {"id": "unique_identifier/usually/base_path"})],
    ),
]


@pytest.mark.parametrize(
    "test_input, arg1, arg2, test_expected", args_to_tuples_correct
)
def test_to_tuples_expected(
    test_input: str, arg1: str, arg2: str, test_expected: str
) -> None:
    """Assert to_tuples() returns correctly."""
    assert list(to_tuples(test_input, arg1, arg2)) == test_expected


def test_to_tuples_output_type():
    """Assert output of to_tuples() is a generator"""
    input_generator = (
        x
        for x in [
            {"title": "This is a title", "id": "base_path"},
            {"title": "This is a second title", "id": "base_path2"},
        ]
    )
    output_generator = to_tuples(input_generator, "title", "id")
    assert isinstance(output_generator, types.GeneratorType)


args_to_tuples_handles_error = [
    ([{}, {}], "title", "id", []),
    ([{}], "title", "id", []),
    ([{}, {"title": "a", "id": 1}], "title", "id", [("a", {"id": 1})]),
]


@pytest.mark.parametrize(
    "test_input, arg1, arg2, test_expected", args_to_tuples_handles_error
)
def test_to_tuples_handles_keyerror(
    test_input: str, arg1: str, arg2: str, test_expected: str
) -> None:
    """Test to_tuples() handles a KeyError correctly."""
    assert list(to_tuples(test_input, arg1, arg2)) == test_expected


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


class TestGzippedCsvToStream:
    """Tests for gzipped_csv_to_stream() function"""

    def test_gzipped_csv_to_stream_output_type(self, in_memory_gzipped_csv):
        """Assert output of gzipped_csv_to_stream() is a generator"""

        assert isinstance(
            gzipped_csv_to_stream(
                in_memory_gzipped_csv, delimiter="\t", skipinitialspace=True
            ),
            types.GeneratorType,
        )

    def test_gzipped_csv_to_stream_correct1(self, in_memory_gzipped_csv):
        """Assert output of gzipped_csv_to_stream() is correct"""

        assert list(
            gzipped_csv_to_stream(
                in_memory_gzipped_csv, delimiter="\t", skipinitialspace=True
            )
        ) == [
            {
                "title": "This is a title",
                "text": "Some text.",
                "stuff": "9876",
                "id": "base_path1",
            },
            {
                "title": "And a second title",
                "text": "More text!",
                "stuff": "1234",
                "id": "base_path2",
            },
        ]

    def test_gzipped_csv_to_stream_correct2(self, in_memory_gzipped_csv):
        """Assert output of gzipped_csv_to_stream() is correct"""

        assert list(
            gzipped_csv_to_stream(
                in_memory_gzipped_csv,
                fields_to_keep=["text", "id"],
                delimiter="\t",
                skipinitialspace=True,
            )
        ) == [
            {"text": "Some text.", "id": "base_path1"},
            {"text": "More text!", "id": "base_path2"},
        ]
