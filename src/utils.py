import datetime as dt
import itertools
from typing import Iterable


def get_day_suffix(day_number: int) -> str:
    """
    Get the suffix portion of a date from the date number, e.g.
    2 -> 'nd', 13 -> 'th'
    """

    if not isinstance(day_number, int):
        raise TypeError("Error in get_day_suffix: 'day_number' argument must be an integer")

    if day_number in itertools.chain(range(4, 21), range(24, 31)):
        return "th"
    return ("st", "nd", "rd")[day_number % 10 - 1]


def get_print_collection_with_indices_str(items: Iterable, start_index: int = 1) -> str:
    """
    Get a string which represented the collection of items, with
    one item per row, and with the index at the start of the row
    """

    max_index_length = len(str(start_index + len(items) - 1))

    ret = ""
    for idx, item in enumerate(items, start_index):
        if idx > start_index:
            ret += "\n"
        ret += f"{idx:<{max_index_length}} - {item}"

    return ret


def get_pretty_print_date_string(
    date: dt.date,
    include_date_number_spacing: bool = False,
    include_year: bool = False
) -> str:
    """
    Get a representation of a date object as, e.g., Wed 5th Jan 2022.

    Args:
    include_date_number_spacing: whether to ensure that the date
        number portion of the returned string has two characters, by
        left-padding numbers less than 10 with a space
    include_year: if true, include the final two characters of the year
    """

    weekday_str = date.strftime("%A")[:3]

    date_number_str = str(date.day)
    if include_date_number_spacing and date.day < 10:
        date_number_str = " " + date_number_str

    date_number_suffix = get_day_suffix(date.day)
    month_str = date.strftime("%B")[:3]

    ret = f"{weekday_str} {date_number_str}{date_number_suffix} {month_str}"

    if include_year:
        ret += f" {date.strftime('%Y')}"

    return ret
