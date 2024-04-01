"""
Add a user-specified (date, meal) pair into the project
diary
"""

from userinputgetter import DateInputGetter, IntegerInputGetter

from mealprep.config import config
from mealprep.meal import Meal, MealDiary
from mealprep.utils import get_print_collection_with_indices_str


MAX_PRINTED_DIARY_ENTRIES = 20


if __name__ == "__main__":
    meal_diary = MealDiary.from_project_diary()
    n_printed_diary_entries = min(len(meal_diary), MAX_PRINTED_DIARY_ENTRIES)
    printed_diary_min_date = sorted(meal_diary.dates)[-n_printed_diary_entries]
    printed_diary = meal_diary.filter_dates(min_date=printed_diary_min_date)
    print("Recent diary:\n")
    print(printed_diary.get_pretty_print_string())

    date_input_getter = DateInputGetter()
    print("\nEnter a date:")
    date = date_input_getter.get_input()
    if date is None:
        exit()

    meal_collection = config.meal_collection
    supported_meal_names = sorted(x.name for x in meal_collection)
    print("\nSupported meals:")
    print(get_print_collection_with_indices_str(supported_meal_names))
    print("\nEnter meal index:")
    meal_index_input_getter = IntegerInputGetter(range(1, len(meal_collection) + 1))
    meal_index = meal_index_input_getter.get_input()
    if meal_index is None:
        exit()
    meal = Meal.from_name(supported_meal_names[meal_index - 1])

    printed_diary[date] = meal
    meal_diary[date] = meal

    print("Updated diary:\n")
    print(printed_diary.get_pretty_print_string())
    print()

    meal_diary.to_project_diary()
