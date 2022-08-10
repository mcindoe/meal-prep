"""
Provides functionality for the creation of shopping lists
"""

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


def combine_ingredients(meal_ingredients: Dict) -> Dict:
    """
    Groups together the ingredients required for all elements of the
    ingeredients iterable into one dictionary representing the total
    quantities required of each key.

    :param ingredients_dict: dict with meals as keys, ingredients
        for each meal as values
    :return: dict with ingredients as keys, value is a dictionary with
        the generating meals list, and the total quantity required
    """
    combined_ingredients = {}
    for meal, ingredients in meal_ingredients.items():
        for ingredient, quantity in ingredients.items():
            if ingredient not in combined_ingredients:
                combined_ingredients[ingredient] = {
                    "required_by": [meal.name],
                    "total": quantity,
                }

            else:
                combined_ingredients[ingredient]["required_by"].append(
                    meal.name
                )
                if get_unit(ingredient) != "bool":
                    combined_ingredients[ingredient]["total"] += quantity

    return combined_ingredients


def make_shopping_list(
    required_ingredients: Dict[str, Dict], filename: Union[Path, str]
) -> None:
    """
    Create a shopping list from the requried ingredients and write to
    file. Ingredients are grouped by category.

    :param required_ingredients: dictionary with ingredients as keys,
        values are dictionaries containing the total quantity required,
        and the meals which require the ingredient. As returned by
        combine_ingredients
    """

    full_ingredients = load_ingredients()
    required_categories = list(
        set([get_category(el) for el in required_ingredients.keys()])
    )

    categorised_list = {
        category: {
            name: info
            for name, info in required_ingredients.items()
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
                required_by = category_entries[name]["required_by"]
                required_by_str = ", ".join(required_by)
                total = category_entries[name]["total"]
                unit = get_unit(name)
                if unit == "bool":
                    fp.write(f"{capitalise(name)}\n\t- {required_by_str}\n")
                elif unit == "units":
                    fp.write(
                        f"{capitalise(name)}: {total}\n\t- {required_by_str}\n"
                    )
                elif unit == "ml":
                    fp.write(
                        f"{capitalise(name)}: {total} ml"
                        f"\n\t- {required_by_str}\n"
                    )
                else:
                    unit_str = unit.capitalize()
                    fp.write(
                        f"{capitalise(name)}: {total} {unit_str} "
                        f"\n\t- {required_by_str}\n"
                    )
