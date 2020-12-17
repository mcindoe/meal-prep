"""
Provides functions to sort data files
"""

from mealprep.src.utils.ingredients import load_ingredients
from mealprep.src.utils.ingredients import write_ingredients
from mealprep.src.utils.meals import load_meals
from mealprep.src.utils.meals import write_meals


def sort_meals() -> None:
    """
    Sort the meals data file
    """

    meals = load_meals()
    sorted_meal_names = sorted(list(meals.keys()))
    sorted_meals = {
        meal_name: meals[meal_name] for meal_name in sorted_meal_names
    }
    write_meals(sorted_meals)


def sort_ingredients() -> None:
    """
    Sort the ingredients data file
    """

    ingredients = load_ingredients()
    sorted_ingredient_names = sorted(list(ingredients.keys()))
    sorted_ingredients = {
        ingredient_name: ingredients[ingredient_name]
        for ingredient_name in sorted_ingredient_names
    }
    write_ingredients(sorted_ingredients)


if __name__ == "__main__":
    sort_ingredients()
    sort_meals()
