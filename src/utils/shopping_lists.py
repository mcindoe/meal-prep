"""
Provides functionality for the creation of shopping lists
"""

from collections.abc import Iterable
from pathlib import Path
from typing import Dict
from typing import Union

from mealprep.src.utils.display import capitalise
from mealprep.src.utils.ingredients import get_category
from mealprep.src.utils.ingredients import get_unit
from mealprep.src.utils.ingredients import load_ingredients

# Order of categories appearing in a shopping list
CATEGORY_ORDER = [
    "vegetable",
    "dairy",
    "carbohydrate",
    "meat",
    "fish",
    "tin",
    "herb",
    "spice",
    "condiment",
    "sauce",
    "other",
]

CATEGORY_TO_HEADER_MAP = {el: el.capitalize() for el in CATEGORY_ORDER}
CATEGORY_TO_HEADER_MAP["vegetable"] = "Vegetables"
CATEGORY_TO_HEADER_MAP["carbohydrate"] = "Carbohydrates"
CATEGORY_TO_HEADER_MAP["tin"] = "Tins"
CATEGORY_TO_HEADER_MAP["herb"] = "Herbs"
CATEGORY_TO_HEADER_MAP["spice"] = "Spices"
CATEGORY_TO_HEADER_MAP["condiment"] = "Condiments"
CATEGORY_TO_HEADER_MAP["sauce"] = "Sauces"


def combine_ingredients(ingredients_iter: Iterable[Dict]) -> Dict:
    """
    Groups together the ingredients required for all elements of the
    ingeredients iterable into one dictionary representing the total
    quantities required of each key.
    """
    combined_ingredients = {}
    for ingredients in ingredients_iter:
        for name, quantity in ingredients.items():
            if name not in combined_ingredients:
                combined_ingredients[name] = quantity

            else:
                if get_unit(name) == "bool":
                    combined_ingredients[name] = True
                else:
                    combined_ingredients[name] += quantity

    return combined_ingredients


def make_shopping_list(
    required_ingredients: Dict, filename: Union[Path, str]
) -> None:
    """
    Create a shopping list from the requried ingredients are write to
    file. Ingredients are grouped by category.
    """
    full_ingredients = load_ingredients()
    required_categories = list(
        set([get_category(el) for el in required_ingredients.keys()])
    )

    categorised_list = {
        category: {
            name: quantity
            for name, quantity in required_ingredients.items()
            if full_ingredients[name]["category"] == category
        }
        for category in required_categories
    }

    sorted_categories = sorted(
        required_categories, key=lambda c: CATEGORY_ORDER.index(c)
    )

    with open(filename, "w+") as fp:
        for idx, category in enumerate(sorted_categories):
            if idx == 0:
                fp.write(f"-- {CATEGORY_TO_HEADER_MAP[category]} --\n")
            else:
                fp.write(f"\n-- {CATEGORY_TO_HEADER_MAP[category]} --\n")

            category_entries = categorised_list[category]
            sorted_category_names = sorted(list(category_entries.keys()))

            for name in sorted_category_names:
                quantity = category_entries[name]
                unit = get_unit(name)
                if unit == "bool":
                    fp.write(f"{capitalise(name)}\n")
                elif unit == "units":
                    fp.write(f"{capitalise(name)}: {quantity}\n")
                elif unit == "ml":
                    fp.write(f"{capitalise(name)}: {quantity} ml\n")
                else:
                    unit_str = unit.capitalize()
                    fp.write(f"{capitalise(name)}: {quantity} {unit_str}\n")
