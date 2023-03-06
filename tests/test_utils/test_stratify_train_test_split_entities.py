import pytest
import json
import srsly
import tempfile
from pathlib import Path

from src.utils.stratify_train_test_split_entities import (
    count_labels_per_class_from_jsonl,
    count_labels_per_class,
    stratify_train_test,
)


@pytest.fixture
def jsonl_file(tmp_path):
    # create a sample jsonl file with two annotations
    sample_data = [
        {
            "text": "foo",
            "spans": [{"start": 0, "end": 3, "label": "LOC"}],
            "answer": "accept",
        },
        {
            "text": "bar",
            "spans": [{"start": 0, "end": 3, "label": "LOC"}],
            "answer": "accept",
        },
        {
            "text": "baz",
            "spans": [{"start": 0, "end": 3, "label": "FAC"}],
            "answer": "accept",
        },
        {
            "text": "loo",
            "spans": [{"start": 0, "end": 3, "label": "FAC"}],
            "answer": "rejected",
        },
    ]
    file_path = tmp_path / "sample.jsonl"
    with open(file_path, "w") as f:
        for item in sample_data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    return file_path


def test_count_labels_per_class_from_jsonl(jsonl_file):
    # Test with a sample file
    expected_counts = sorted([("LOC", 2), ("FAC", 1)])
    assert count_labels_per_class_from_jsonl(jsonl_file) == expected_counts

    # Test with an empty file
    empty_file = jsonl_file.with_name("empty.jsonl")
    empty_file.touch()
    assert count_labels_per_class_from_jsonl(empty_file) == []

    # Test with a non-existing file
    with pytest.raises(ValueError):
        count_labels_per_class_from_jsonl(Path("non_existing_file.jsonl"))

    # Test with an invalid file type
    with pytest.raises(ValueError):
        count_labels_per_class_from_jsonl(jsonl_file.with_suffix(".txt"))


def test_count_labels_per_class_empty_file():
    assert count_labels_per_class([]) == []


def test_count_labels_per_class_single_label():
    data = [
        {"text": "foo", "spans": [{"start": 0, "end": 3, "label": "LOC"}]},
    ]
    assert count_labels_per_class(data) == [("LOC", 1)]


def test_count_labels_per_class_multiple_labels():
    data = [
        {"text": "foo", "spans": [{"start": 0, "end": 3, "label": "LOC"}]},
        {"text": "bar", "spans": [{"start": 0, "end": 3, "label": "LOC"}]},
        {"text": "baz", "spans": [{"start": 0, "end": 3, "label": "SECTOR"}]},
        {"text": "qux", "spans": [{"start": 0, "end": 3, "label": "FAC"}]},
        {"text": "quux", "spans": [{"start": 0, "end": 3, "label": "FAC"}]},
    ]
    assert count_labels_per_class(data) == [("SECTOR", 1), ("FAC", 2), ("LOC", 2)]


@pytest.fixture
def example_jsonl(tmpdir_factory):
    tmp_file = tmpdir_factory.mktemp("data").join("example.jsonl")
    with open(tmp_file, "w") as f:
        f.write(
            '{"text": "foo", "spans": [{"start": 0, "end": 3, "label": "LOC"}], "answer": "accept"}\n'
        )
        f.write(
            '{"text": "fra", "spans": [{"start": 0, "end": 3, "label": "LOC"}], "answer": "accept"}\n'
        )
        f.write(
            '{"text": "fru", "spans": [{"start": 0, "end": 3, "label": "LOC"}], "answer": "accept"}\n'
        )
        f.write(
            '{"text": "fez", "spans": [{"start": 0, "end": 3, "label": "LOC"}], "answer": "accept"}\n'
        )
        f.write(
            '{"text": "bar", "spans": [{"start": 0, "end": 3, "label": "SECTOR"}], "answer": "accept"}\n'
        )
        f.write(
            '{"text": "bru", "spans": [{"start": 0, "end": 3, "label": "SECTOR"}], "answer": "accept"}\n'
        )
        f.write(
            '{"text": "bor", "spans": [{"start": 0, "end": 3, "label": "SECTOR"}], "answer": "accept"}\n'
        )
        f.write(
            '{"text": "bat", "spans": [{"start": 0, "end": 3, "label": "SECTOR"}], "answer": "accept"}\n'
        )

    return str(tmp_file)


def test_stratify_train_test(example_jsonl):
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir)

        stratify_train_test(
            input_path=example_jsonl, folder_output_path=output_path, test_size=0.25
        )

        # check that both files exist
        assert (output_path / "data_train.jsonl").is_file()
        assert (output_path / "data_test.jsonl").is_file()

        # check that the size of train and test set is correct
        train_set = list(srsly.read_jsonl(output_path / "data_train.jsonl"))
        test_set = list(srsly.read_jsonl(output_path / "data_test.jsonl"))
        assert len(train_set) == 6
        assert len(test_set) == 2

        # check that the labels are counted correctly
        expected_labels_train = [("LOC", 3), ("SECTOR", 3)]
        expected_labels_test = [("LOC", 1), ("SECTOR", 1)]
        assert count_labels_per_class(train_set) == expected_labels_train
        assert count_labels_per_class(test_set) == expected_labels_test
