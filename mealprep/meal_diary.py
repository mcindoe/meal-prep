from __future__ import annotations

import copy
import datetime as dt
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Optional, Tuple

from mealprep.loc import PROJECT_MEAL_DIARY_FILE_PATH
from mealprep.meal import Meal
from mealprep.meal_collection import MealCollection
from mealprep.recipe.reading import get_meal_from_name
from mealprep.utils import get_pretty_print_date_string


class MealDiary:
    DATE_FORMAT = "%Y-%m-%d"

    def __init__(self, meal_diary: Optional[dict[dt.date, Meal]] = None):
        if meal_diary is not None:
            if not isinstance(meal_diary, dict):
                raise TypeError("meal_diary, if specified, must be a dictionary in MealDiary init")

        if meal_diary is None:
            self.meal_diary = dict()
        else:
            self.meal_diary = meal_diary.copy()

        if not all(isinstance(x, dt.date) for x in self.meal_diary):
            raise TypeError("All keys of 'meal_diary' must be datetime.dates in MealDiary init")

        if not all(isinstance(x, Meal) for x in self.meal_diary.values()):
            raise TypeError("All values of 'meal_diary' must be Meal instances")

    def copy(self) -> MealDiary:
        return MealDiary(copy.copy(self.meal_diary))

    def __getitem__(self, date: dt.date) -> Meal:
        if not isinstance(date, dt.date):
            raise TypeError("Key must be date in MealDiary.__getitem__")

        return self.meal_diary[date]

    def __setitem__(self, date: dt.date, meal: Meal) -> None:
        if not isinstance(date, dt.date):
            raise TypeError("Key must be date in MealDiary.__getitem__")
        if not isinstance(meal, Meal):
            raise TypeError("value must be a Meal in MealDiary.__getitem__")

        self.meal_diary[date] = meal

    @property
    def dates(self) -> Tuple[dt.date, ...]:
        return tuple(self.meal_diary.keys())

    @property
    def meals(self) -> MealCollection:
        return MealCollection(self.meal_diary.values())

    def items(self):
        return self.meal_diary.items()

    def get_representation(self) -> dict[str, str]:
        """
        Represent the instance as a dictionary mapping date strings to
        meal names
        """

        ret = {date.strftime(MealDiary.DATE_FORMAT): meal.name for date, meal in self.items()}
        return dict(sorted(ret.items()))

    def __repr__(self) -> str:
        return str(self.get_representation())

    def __bool__(self) -> bool:
        return len(self.meal_diary) > 0

    def __eq__(self, other: MealDiary) -> bool:
        if not isinstance(other, MealDiary):
            return False

        return self.meal_diary == other.meal_diary

    def __len__(self) -> int:
        return len(self.meal_diary)

    def to_file(self, file_path: Path):
        with open(file_path, "w+") as fp:
            json.dump(self.get_representation(), fp, indent=2)

    @staticmethod
    def from_file(file_path: Path) -> MealDiary:
        try:
            with open(file_path, "r") as fp:
                dict_representation = json.load(fp)
        except FileNotFoundError:
            raise ValueError(f'Specified file "{file_path}" could not be found')
        except json.decoder.JSONDecodeError:
            raise ValueError(f'Specified file "{file_path}" could not be parsed into JSON')

        return MealDiary(
            {
                dt.datetime.strptime(date_string, MealDiary.DATE_FORMAT).date(): get_meal_from_name(
                    meal_name
                )
                for date_string, meal_name in dict_representation.items()
            }
        )

    def to_project_diary(self) -> None:
        self.to_file(PROJECT_MEAL_DIARY_FILE_PATH)

    @staticmethod
    def from_project_diary() -> MealDiary:
        return MealDiary.from_file(PROJECT_MEAL_DIARY_FILE_PATH)

    def upsert(self, other: MealDiary) -> MealDiary:
        return MealDiary(self.meal_diary | other.meal_diary)

    def difference(self, other: MealDiary) -> MealDiary:
        return MealDiary(
            {
                date: meal
                for date, meal in self.meal_diary.items()
                if date not in other.meal_diary.keys()
            }
        )

    def filter_by_time_delta(self, date: dt.date, time_delta: dt.timedelta) -> MealDiary:
        return MealDiary(
            {
                meal_date: meal
                for meal_date, meal in self.items()
                if abs(meal_date - date) <= time_delta
            }
        )

    def filter_dates(self, min_date: dt.date, max_date: Optional[dt.date] = None) -> MealDiary:
        """
        Return a copy of the subset of the MealDiary with keys between
        the start_date (inclusive) and end_date (exclusive)

        If max_date is not specified, then return a copy of the subset
        of the MealDiary with keys and date >= the specified start_date
        """

        if not isinstance(min_date, dt.date):
            raise TypeError("min_date must be a datetime.date")

        if max_date is not None:
            if not isinstance(max_date, dt.date):
                raise TypeError("max_date must be a datetime.date")

        if max_date is None:
            return MealDiary(
                {meal_date: meal for meal_date, meal in self.items() if meal_date >= min_date}
            )

        return MealDiary(
            {
                meal_date: meal
                for meal_date, meal in self.items()
                if meal_date >= min_date
                if meal_date < max_date
            }
        )

    def except_dates(self, dates_to_exclude: Iterable[dt.date]) -> MealDiary:
        """
        Return a copy of the MealDiary with the specified dates removed
        (if present)
        """

        if isinstance(dates_to_exclude, dt.date):
            dates_to_exclude = (dates_to_exclude,)

        dates_to_exclude = set(x for x in dates_to_exclude)

        if not all(isinstance(x, dt.date) for x in dates_to_exclude):
            raise TypeError("All passed dates must be datetime.dates")

        return MealDiary(
            {
                meal_date: meal
                for meal_date, meal in self.items()
                if meal_date not in dates_to_exclude
            }
        )

    def get_pretty_print_string(self) -> str:
        include_date_number_spacing = any(x.day >= 10 for x in self.dates)
        include_year = len(set(x.year for x in self.dates)) > 1

        lines = []
        for date in sorted(self.dates):
            meal = self[date]
            date_str = get_pretty_print_date_string(date, include_date_number_spacing, include_year)
            lines.append(f"{date_str}: {meal.name}")

        return "\n".join(lines)

    def filter_by_max_before_and_max_after_today(
        self,
        max_printed_previous_diary_entries: int,
        max_printed_next_diary_entries: int,
    ) -> MealDiary:
        """
        Return a copy of this MealDiary, filtered to only dates which are close to
        today, specifically the 'max_printed_previous_diary_entries' closest before
        today, and the 'max_printed_next_diary_entries' closest after today
        """

        previous_dates = sorted([x for x in self.dates if x < dt.date.today()])
        if previous_dates:
            n_previous_dates_printed = min(len(previous_dates), max_printed_previous_diary_entries)
            if n_previous_dates_printed > 0:
                min_printed_date = previous_dates[-n_previous_dates_printed]
            else:
                min_printed_date = dt.date.today()
        else:
            min_printed_date = dt.date.today()

        next_dates = sorted([x for x in self.dates if x >= dt.date.today()])
        if next_dates:
            n_next_dates_printed = min(len(next_dates), max_printed_next_diary_entries)
            if n_next_dates_printed > 0:
                max_printed_date = next_dates[n_next_dates_printed - 1]
            else:
                max_printed_date = dt.date.today()
        else:
            max_printed_date = None

        return self.filter_dates(min_date=min_printed_date, max_date=max_printed_date)
