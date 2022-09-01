import pytest
from datetime import datetime
from src.utils.helpers_formatting import shorten_date_format

args_shorten_date_format_correct = [
    ("2022-11-03", "031122"),
    (datetime.strptime("2022-11-03", "%Y-%m-%d").date(), "031122"),
]


@pytest.mark.parametrize("test_input, test_expected", args_shorten_date_format_correct)
def test_shorten_date_format(test_input: str, test_expected: str) -> None:
    """Assert the ``shorten_date_format`` returns correctly."""
    assert shorten_date_format(test_input) == test_expected


def test_shorten_date_format_raises_valuerror() -> None:
    """Test shorten_date_format raises a ValueError if given a ill-formatted string."""
    with pytest.raises(ValueError):
        assert shorten_date_format("2002/03/17")
        assert shorten_date_format("2002-02-44")
