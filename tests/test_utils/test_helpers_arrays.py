import pytest
from typing import List, Union
from src.utils.helpers_arrays import flatten_list_of_lists
from src.utils.helpers_arrays import flatten_list_of_str_dict

args_flatten_list_of_lists = [
    ([["a", "b", "c"], ["r"], ["s", "d"]], ["a", "b", "c", "r", "s", "d"]),
    ([["a", "b", "c"], [], ["s", "d"]], ["a", "b", "c", "s", "d"]),
    ([["a", "b", "c"], [""], ["s", "d"]], ["a", "b", "c", "s", "d"]),
    ([["a", "b", "c"], "r", ["s", "d"]], ["a", "b", "c", "r", "s", "d"]),
    ([["a", "b", "c"], None, ["s", "d"]], ["a", "b", "c", "s", "d"]),
]


@pytest.mark.parametrize("test_input, test_expected", args_flatten_list_of_lists)
def test_flatten_list_of_lists(
    test_input: List[list], test_expected: List[str]
) -> None:
    """Assert the ``flatten_list_of_lists`` returns correctly."""
    assert flatten_list_of_lists(test_input) == test_expected


args_flatten_list_of_str_dict = [
    ([{"a": "1", "b": "2", "c": "3"}, "s", "d"], ["1", "2", "3", "s", "d"]),
    (
        [{"a": "1", "b": "2", "c": "3"}, {"a": "1", "b": "2", "c": "3"}, "1", "2"],
        ["1", "2", "3", "1", "2", "3", "1", "2"],
    ),
]


@pytest.mark.parametrize("test_input, test_expected", args_flatten_list_of_str_dict)
def test_flatten_list_of_str_dict(
    test_input: List[Union[str, dict]], test_expected: List[str]
) -> None:
    """Assert the ``flatten_list_of_str_dict`` returns correctly."""
    assert flatten_list_of_str_dict(test_input) == test_expected
