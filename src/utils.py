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
