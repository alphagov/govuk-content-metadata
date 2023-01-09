import pytest
import types
import gzip
from io import BytesIO


from bulk_inference_pipeline.src.utils import chunks


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
