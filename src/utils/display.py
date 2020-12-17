"""
Provides utilities relating to neatly presenting or displaying
information
"""

import calendar
import datetime as dt
from typing import Dict
from typing import List

from mealprep.src.utils.meals import Meal


def make_date_string(date: dt.date) -> str:
    """
    Format a dt.date instance in the following format

    Example: dt.date(2020, 11, 22) -> Sun, 22nd of Nov
    """
    day_str = calendar.day_name[date.weekday()][:3]
    month_str = calendar.month_name[date.month][:3]

    if 4 < date.day <= 20 or 24 <= date.day <= 30:
        day_suffix = "th"
    else:
        day_suffix = ["st", "nd", "rd"][date.day % 10 - 1]

    return f"{day_str}, {date.day}{day_suffix} of {month_str}"


def print_history(history: Dict[dt.date, Meal], with_index: bool = False):
    """
    Neatly prints a history dictionary.

    Default behaviour is to format
    the date and print the meal description alongside. An optional
    with_index parameter is provided to print indices along the
    left-hand-side to allow users to easily refer to parts of the
    history when making choices.

    :history: Dict[dt.date, Meal] - the history to be printed
    :with_index: bool - whether to print indices alongside the history
    """

    sorted_dates = sorted(list(history.keys()))
    date_strings = [make_date_string(date) for date in sorted_dates]
    longest_date_str_len = max([len(date_str) for date_str in date_strings])

    if with_index:
        largest_index_len = len(str(len(history) + 1))

    for idx, (date, date_str) in enumerate(zip(sorted_dates, date_strings)):
        recommended_meal = history[date]
        if with_index:
            print(
                "{0: <{1}} {2: <{3}} - {4}".format(
                    idx + 1,
                    largest_index_len,
                    date_str,
                    longest_date_str_len,
                    recommended_meal,
                )
            )
        else:
            print(
                "{0: <{1}} - {2}".format(
                    date_str, longest_date_str_len, recommended_meal
                )
            )


def make_list_str(elements: List[str]) -> str:
    """
    Format a list of strings in to a list separated by commas
    and 'and's as a human would write:

    Examples:
    [itemA, itemB] -> "itemA and itemB"
    [itemA, itemB, itemC] -> "itemA, itemB and itemC"
    """

    if not elements:
        return ""

    if len(elements) == 1:
        return str(elements[0])

    first_elements = elements[:-1]
    last_element = elements[-1]
    return f'{", ".join(first_elements)} and {last_element}'


def capitalise(input_str: str) -> str:
    """
    Capitalise all words in the input string
    """

    words = input_str.split(" ")
    return " ".join([word.capitalize() for word in words])


def get_day_name(day_number: int) -> str:
    """
    Return the name of the weekday with index day_number
    """

    return list(calendar.day_name)[day_number]
