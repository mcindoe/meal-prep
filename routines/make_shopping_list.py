"""
Make a shopping list for the meals in the project
diary between the user-specified dates
"""


import datetime as dt
from userinputgetter import DateInputGetter

from mealprep.src.config import config
from mealprep.src.loc import SHOPPING_LIST_DIR
from mealprep.src.meal import MealDiary
from mealprep.src.shopping_list import ShoppingList


MAX_PRINTED_PREVIOUS_DIARY_ENTRIES = 5
MAX_PRINTED_NEXT_DIARY_ENTRIES = 15


def make_shopping_list(start_date: dt.date, end_date: dt.date) -> None:
    """
    Create a shopping list for the meals in the project
    diary between start_date and end_date (inclusive)
    """

    meal_diary = MealDiary.from_project_diary()
    filtered_diary = meal_diary.filter_dates(
        min_date=start_date,
        max_date=end_date + dt.timedelta(days=1)
    )

    if not filtered_diary:
        print("\nProject diary has no dates in the specified range\n")
        return

    shopping_list = ShoppingList(filtered_diary.meals)
    shopping_list_filename = shopping_list.get_filename(start_date, end_date)
    shopping_list_filepath = SHOPPING_LIST_DIR / shopping_list_filename

    print(f"\nCreating shopping list at\n{shopping_list_filepath}\n")
    shopping_list.to_file(shopping_list_filepath)


if __name__ == "__main__":
    meal_diary = MealDiary.from_project_diary()

    if not meal_diary:
        print("Project meal diary is empty, so nothing to do")
        exit()

    printed_diary = meal_diary.filter_by_max_before_and_max_after_today(
        MAX_PRINTED_PREVIOUS_DIARY_ENTRIES,
        MAX_PRINTED_NEXT_DIARY_ENTRIES
    )

    if printed_diary:
        print("Recent diary:\n")
        print(printed_diary.get_pretty_print_string())

    date_input_getter = DateInputGetter()

    print("\nEnter start date:")
    start_date = date_input_getter.get_input()
    if start_date is None:
        exit()

    print("\nEnter end date:")
    end_date = date_input_getter.get_input()
    if end_date is None:
        exit()

    make_shopping_list(start_date, end_date)
