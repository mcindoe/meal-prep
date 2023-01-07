"""
Print ingredients by category. Search for spelling mistakes, bad category
assignments etc
"""

from typing import Dict
from typing import Tuple

from mealprep.src.constants import Category
from mealprep.src.ingredient import Ingredient
from mealprep.src.ingredient import Ingredients


def get_ingredients_by_category() -> Dict[Category, Tuple[Dict[str, str]]]:
    """
    Get a dictionary mapping categories to all known ingredients of that
    category
    """

    ret = {}
    for x in Ingredients:
        category = x.value.category

        if category not in ret:
            ret[category] = []

        ret[category].append({
            "enum_name": x.name,
            "ingredient_name": x.value.name,
        })

    return ret


if __name__ == "__main__":
    ingredients_by_category = get_ingredients_by_category()

    # Sort dictionary by the order the categories appear in a shopping list
    ingredients_by_category = {
        category: ingredients_by_category[category]
        for category in sorted(
            ingredients_by_category.keys(),
            key=lambda x: x.order
        )
    }

    print()

    for category, category_ingredient_names in ingredients_by_category.items():
        category_ingredient_names = sorted(
            category_ingredient_names,
            key=lambda x: x["enum_name"]
        )

        print(f"{category.list_header}:")
        for x in category_ingredient_names:
            print(f"\t{x['enum_name']} - {x['ingredient_name']}")
        print()
