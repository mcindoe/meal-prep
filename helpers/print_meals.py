"""
For ingredients and metadata associated with meals, as well as whether
the meal is included in the project config collection
"""


from mealprep.src.config import config
from mealprep.src.meal import Meal
from mealprep.src.meal import Meals
from mealprep.src.shopping_list import ShoppingList


def print_meal_information(meal: Meal, enum_name: str) -> None:
    print(f"{meal.name}:")
    print(f"\tEnum name - {enum_name}")
    print(f"\tIn project config - {meal in config.meals}")

    print(f"\tIngredients:")
    for x in meal.ingredient_quantities:
        ingredient_quantity_description = ShoppingList.get_ingredient_quantity_description((x,))
        if ingredient_quantity_description is None:
            print(f"\t\t{x.ingredient.name}")
        else:
            print(f"\t\t{x.ingredient.name} - {ingredient_quantity_description}")

    print(f"\tMetadata:")
    for k, v in meal.metadata.items():
        print(f"\t\t{k!r} - {v!r}")


if __name__ == "__main__":
    print()
    for x in Meals:
        print_meal_information(x.value, x.name)
        print()
