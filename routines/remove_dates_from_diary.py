"""
Remove user-specified dates from the project diary
"""


import datetime as dt
from userinputgetter import DateInputGetter

from mealprep.src.config import config
from mealprep.src.meal import MealDiary


MAX_PRINTED_PREVIOUS_DIARY_ENTRIES = 15
MAX_PRINTED_NEXT_DIARY_ENTRIES = 5


if __name__ == "__main__":
    meal_diary = MealDiary.from_project_diary()

    if not meal_diary:
        print("Project meal diary is empty, so nothing to do")
        exit()

    previous_dates = sorted([x for x in meal_diary.dates if x < dt.date.today()])
    if previous_dates:
        n_previous_dates_printed = min(len(previous_dates), MAX_PRINTED_PREVIOUS_DIARY_ENTRIES)
        if n_previous_dates_printed > 0:
            min_printed_date = previous_dates[-n_previous_dates_printed]
        else:
            min_printed_date = dt.date.today()
    else:
        min_printed_date = dt.date.today()

    next_dates = sorted([x for x in meal_diary.dates if x >= dt.date.today()])
    if next_dates:
        n_next_dates_printed = min(len(next_dates), MAX_PRINTED_NEXT_DIARY_ENTRIES)
        if n_next_dates_printed > 0:
            max_printed_date = next_dates[n_next_dates_printed - 1]
        else:
            max_printed_date = dt.date.today()
    else:
        max_printed_date = None

    printed_diary = meal_diary.filter_dates(min_date=min_printed_date, max_date=max_printed_date)

    if printed_diary:
        print("Recent diary:\n")
        print(printed_diary.get_pretty_print_string())

    date_input_getter = DateInputGetter(meal_diary.dates)
    print("\nEnter dates to remove from the meal diary")
    dates_to_remove = date_input_getter.get_multiple_inputs()
    if dates_to_remove is None:
        exit()

    printed_diary = printed_diary.except_dates(dates_to_remove)
    meal_diary = meal_diary.except_dates(dates_to_remove)

    if printed_diary:
        print("\nUpdated diary:\n")
        print(printed_diary.get_pretty_print_string())
    else:
        print("\nDates removed")

    meal_diary.to_project_diary()
    print()
