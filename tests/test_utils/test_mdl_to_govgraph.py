import pytest
import pandas as pd
from io import BytesIO
from src.utils.mdl_to_govgraph import (
    jsonl_to_csv_wrangle,
    # process_and_save_files,
    # concatenate_csv_per_unit,
    # load_merge_csv_files,
    contains_alphanum,
    is_latin,
    only_roman_chars,
    # preprocess_merged_df,
)


def test_jsonl_to_csv_wrangle_output_type():
    """Assert error raised if bad input name."""
    with pytest.raises(ValueError):
        assert jsonl_to_csv_wrangle(
            in_jsonl="badname.jsonl", out_jsonl="finename.jsonl"
        )
        assert jsonl_to_csv_wrangle(
            in_jsonl="anothername.jsonl", out_jsonl="finename.jsonl"
        )


# # tests for process_and_save_files()
# def test_process_and_save_files():

# # tests for concatenate_csv_per_unit()
# def test_concatenate_csv_per_unit():

# mock a gzipped csv file
mock_rows_byte = b"base_path\tentity_inst\tentity_type\tdescription_weight\n\
    /some path \tSome text.\tORG\t1\n\
    /another/path\tMore text!\tPER\t2"


@pytest.fixture()
def in_memory_csv():
    stream = BytesIO()
    with open(stream, "wb") as f:
        f.write(mock_rows_byte)
    stream.seek(0)
    return stream


# tests for load_merge_csv_files()
class TestLoadMergeCsvFiles:
    """Tests for load_merge_csv_files function"""

    def test_load_merge_csv_files(self, in_memory_csv):
        """Assert output of test_load_merge_csv_files is DataFrame"""

        assert isinstance(in_memory_csv, pd.DataFrame)


# tests contains_alphanum()
@pytest.mark.parametrize(
    "string, bool",
    [
        ("hello world", True),
        ("المملكة", True),
        ("Привет 123", True),
        ("***", False),
        ("hello []9", True),
        ("[]';]", False),
    ],
)
def test_contains_alphanum(string, bool):
    assert contains_alphanum(string) == bool


# tests is_latin()
@pytest.mark.parametrize(
    "char, bool",
    [
        ("h", True),
        ("w", True),
        ("ت", False),
        ("и", False),
        ("*", False),
        ("9", False),
        ("á", True),
    ],
)
def test_is_latin(char, bool):
    assert is_latin(char) == bool


# tests only_roman_chars()
@pytest.mark.parametrize(
    "string, bool",
    [
        ("hello", True),
        ("world", True),
        ("naïve", True),
        ("hello Россия", False),
        ("Hello, Zhōngguó", True),
        ("Hello, 中国人", False),
        ("المملكة العربية السعودية", False),
    ],
)
def test_only_roman_chars(string, bool):
    assert only_roman_chars(string) == bool
