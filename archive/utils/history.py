"""
Provides utilities relating to working with history dictionaries and the
history data file
"""

import datetime as dt
import json
from collections.abc import Iterable
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from mealprep.config import DATA
from mealprep.config import JSON_INDENT
from mealprep.src.utils.meals import Meal

HISTORY_FILE = DATA / "history.json"


def filter_history(
    history: Dict[dt.date, Meal],
    start: Optional[dt.date] = None,
    end: Optional[dt.date] = None,
) -> Dict[dt.date, Meal]:

    """
    Filter a history dictionary, returning a sub-dictionary which is
    on or after the start date, and strictly before the end date. Both
    sides are optional.

    :history: datetime objects pointing to Meal instances
    :start: if specified, only history on or after this date are
        returned
    :end: if specified, only history strictly before this date are
        returned
    """

    if start is not None:
        history = {
            date: entry for date, entry in history.items() if date >= start
        }

    if end is not None:
        history = {
            date: entry for date, entry in history.items() if date < end
        }

    return history


def load_history(
    start: Optional[dt.date] = None, end: Optional[dt.date] = None
) -> Dict[dt.date, Meal]:

    """
    Reads the history information from JSON data file, converting to
    a dictionary of dt.dates pointing to Meal instances. Optional
    filtering by dates.

    :start: if specified, only history recorded on or after this date
        are returned
    :end: if specified, only history recorded strictly before this date
        are returned
    """

    with open(HISTORY_FILE, "r") as fp:
        json_history = json.load(fp)

    history = {}
    for date_str, meal_info in json_history.items():
        year, month, day = [int(el) for el in date_str.split("/")]
        date = dt.date(year, month, day)

        history[date] = Meal.from_json(meal_info)

    return filter_history(history, start, end)


def overwrite_history(history: Dict[dt.date, Meal]) -> None:
    """
    Overwrite the history data file with the specified history, written
    as JSON.

    The history argument is expected to be a dictionary of dt.dates
    which point to Meal instances.
    """

    json_history = {}
    for date, meal in history.items():
        date_str = date.strftime("%Y/%m/%d")
        json_history[date_str] = meal.to_json()

    sorted_keys = sorted(json_history.keys())
    sorted_history = {
        date_str: json_history[date_str] for date_str in sorted_keys
    }

    with open(HISTORY_FILE, "w") as fp:
        json.dump(sorted_history, fp, indent=JSON_INDENT)


def add_history_entry(date: dt.date, meal: Meal) -> None:
    """
    Add a single history entry to the history data file
    """

    history = load_history()
    history[date] = meal
    overwrite_history(history)


def add_history_entries(additional_history: Dict[dt.date, Meal]) -> None:
    """
    Add all history entries specified in the additional_history
    dictionary to the history data file
    """

    history = load_history()
    sorted_dates = sorted(list(additional_history.keys()))
    for date in sorted_dates:
        history[date] = additional_history[date]
    overwrite_history(history)


def delete_history_entries(dates: Union[dt.date, Iterable[dt.date]]) -> None:
    """
    Delete the entries corresponding to the specified dates argument
    from the history data file.

    :param date: either a dt.date or an iterable of dt.dates
    """

    if isinstance(dates, dt.date):
        dates = [dates]

    history = load_history()
    history = {d: entry for d, entry in history.items() if d not in dates}
    overwrite_history(history)


def delete_history_window(start_date: dt.date, end_date: dt.date) -> None:
    """
    Delete all entries from the history data file which fall in the
    specified window. End date is not included in the window.
    """

    history = load_history()
    filtered_history = {
        d: entry
        for d, entry in history.items()
        if d < start_date or d >= end_date
    }
    overwrite_history(filtered_history)


def get_close_history(
    history: Dict[dt.date, Meal], pivot: dt.date, n_days: int
) -> Dict[dt.date, Meal]:
    """
    Get history entries which are within n_days days of the pivot date
    """

    start = pivot - dt.timedelta(days=n_days)
    end = pivot + dt.timedelta(days=n_days + 1)
    return filter_history(history, start, end)


def get_history_meal_names(history: Dict[dt.date, Meal]) -> List[str]:
    """
    Get all meal names appearing in a given history
    """

    return [meal.name for meal in history.values()]


def get_close_history_meal_names(
    history: Dict[dt.date, Meal], pivot: dt.date, n_days: int
) -> List[str]:

    """
    Get the meal names of all meals appearing within n_days, inclusive,
    of the specified pivot, in the specified history
    """

    close_history = get_close_history(history, pivot, n_days)
    return get_history_meal_names(close_history)
