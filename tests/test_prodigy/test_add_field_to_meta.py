import pytest
from src.prodigy.add_field_to_meta import add_field_to_meta

in_json_list = [
    {"text": "This is text 1", "meta": {"base_path": "base_path 1", "hash": "hash1"}},
    {"text": "This is text 2"},
    {"text": "This is text 3", "meta": {"base_path": "base_path 3", "hash": "hash3"}},
]

out_json_list = [
    {"text": "This is text 1", "meta": {"base_path": "base_path 1", "hash": "hash1"}},
    {"text": "This is text 2", "meta": {"base_path": "unknown"}},
    {"text": "This is text 3", "meta": {"base_path": "base_path 3", "hash": "hash3"}},
]

args_correct = [(in_json_list, out_json_list)]


@pytest.mark.parametrize("in_json_list, out_json_list", args_correct)
def test_correct_add_field_to_meta(in_json_list, out_json_list):
    """Assert the ``add_field_to_meta`` returns correctly."""
    assert add_field_to_meta(in_json_list) == out_json_list
