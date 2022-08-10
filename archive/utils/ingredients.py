"""
Provides utilities relating to working with ingredients dictionaries and
the history data file
"""

import json
from typing import Dict

from mealprep.config import DATA
from mealprep.config import JSON_INDENT

INGREDIENTS_FILE = DATA / "ingredients.json"


def load_ingredients() -> Dict:
    """
    Read the dictionary of supported ingredients from file
    """

    with open(INGREDIENTS_FILE, "r") as fp:
        ingredients = json.load(fp)
    return ingredients


def write_ingredients(ingredients: Dict) -> None:
    """
    Overwrite the ingredients data file with a dictionary of ingredients
    """

    with open(INGREDIENTS_FILE, "w") as fp:
        json.dump(ingredients, fp, indent=JSON_INDENT)


def get_category(ingredient: str) -> str:
    """
    Get the category the specified ingredient is part of
    """

    ingredients = load_ingredients()
    assert ingredient in ingredients
    return ingredients[ingredient]["category"]


def get_unit(ingredient: str) -> str:
    """
    Get the unit the specified ingredient is measured in
    """

    ingredients = load_ingredients()
    assert ingredient in ingredients
    return ingredients[ingredient]["measured_in"]
