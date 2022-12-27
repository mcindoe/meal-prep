"""
Read the config file to determine supported meals, rules to
apply, and the dates to recommend a meal plan for; then
continuously generate and recommend meal plans until the user
is satisfied (or exists the program); write the updated diary
to file and generate a shopping list
"""


import datetime as dt
from typing import Iterable

from mealprep.src.config import config
from mealprep.src.loc import SHOPPING_LIST_DIR
from mealprep.src.meal import MealCollection
from mealprep.src.meal import MealDiary
from mealprep.src.meal_selector import MealSelector
from mealprep.src.shopping_list import ShoppingList


if __name__ == "__main__":
    meal_collection = config.meal_collection
    rule_collection = config.rule_collection
    meal_diary = MealDiary.from_project_diary()
    meal_selector = MealSelector(
        meal_collection,
        rule_collection,
        meal_diary
    )

    dates = config.dates
    diary_additions = meal_selector.recommend_until_confirmed(dates)

    if diary_additions is None:
        exit()

    new_diary = meal_diary.upsert(diary_additions)
    new_diary.to_project_diary()

    shopping_list = ShoppingList(diary_additions.meals)
    shopping_list_filename = shopping_list.get_filename(min(dates), max(dates))
    shopping_list.to_file(SHOPPING_LIST_DIR / shopping_list_filename)

    print("\nBon Appetit!\n")
