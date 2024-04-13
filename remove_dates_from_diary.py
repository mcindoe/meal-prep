"""
Remove user-specified dates from the project diary
"""

from userinputgetter import DateInputGetter

from mealprep.meal_diary import MealDiary


MAX_PRINTED_PREVIOUS_DIARY_ENTRIES = 15
MAX_PRINTED_NEXT_DIARY_ENTRIES = 5


if __name__ == "__main__":
    meal_diary = MealDiary.from_project_diary()

    if not meal_diary:
        print("Project meal diary is empty, so nothing to do")
        exit()

    printed_diary = meal_diary.filter_by_max_before_and_max_after_today(
        MAX_PRINTED_PREVIOUS_DIARY_ENTRIES, MAX_PRINTED_NEXT_DIARY_ENTRIES
    )

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
