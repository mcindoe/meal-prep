from utils import load_meals
from utils import write_meal_entries


def sort_meals():
    meals = load_meals()
    sorted_meal_names = sorted(list(meals.keys()))
    sorted_meals = {
        meal_name: meals[meal_name]
        for meal_name in sorted_meal_names
    }
    write_meals(sorted_meals)


def sort_ingredients():
    ingredients = load_ingredients()
    sorted_ingredient_names = sorted(list(ingredients.keys()))
    sorted_ingredients = {
        ingredient_name: ingredients[ingredient_name]
        for ingredient_name in sorted_ingredient_names
    }
    write_ingredients_sorted_ingredients


if __name__ == '__main__':
    sort_ingredients()
    sort_meals()
