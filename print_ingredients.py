"""
Print ingredients by category. Search for spelling mistakes, bad category
assignments etc
"""

from mealprep.constants import Category
from mealprep.ingredient import Ingredient


def get_ingredients_by_category() -> dict[Category, list[str]]:
    """
    Get a dictionary mapping categories to all known ingredients of that
    category
    """

    ret = {}
    for ingredient_name, ingredient_info in Ingredient.SUPPORTED_INGREDIENT_INFO.items():
        category = Category[ingredient_info["category"]]

        if category not in ret:
            ret[category] = []

        ret[category].append(ingredient_name)

    ret = {category: sorted(ingredient_names) for category, ingredient_names in ret.items()}

    return ret


if __name__ == "__main__":
    ingredients_by_category = get_ingredients_by_category()

    # Sort dictionary by the order the categories appear in a shopping list
    ingredients_by_category = {
        category: ingredients_by_category[category]
        for category in sorted(ingredients_by_category.keys(), key=lambda category: category.order)
    }

    print()

    for category, category_ingredient_names in ingredients_by_category.items():
        print(f"{category.list_header}:")
        print("\n".join("\t" + name for name in category_ingredient_names))
        print()
