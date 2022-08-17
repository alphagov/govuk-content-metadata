from datetime import date
from typing import Union


def shorten_date_format(date_original: Union[date, str]) -> str:
    """
    Reformat a date in format "YYYY-MM-DD" into "DDMMYY" which aligns with what is
    expected by the preprocessed_content_store_{DDMMYY} filename.

    Args:
        date_original: date in "YYYY-MM-DD"
    Returns:
        the same data as "DDMMYY"
    """
    elements_array = str(date_original).split("-")
    return elements_array[2] + elements_array[1] + elements_array[0][2:]


# shorten_date_format("2022-07-20")
