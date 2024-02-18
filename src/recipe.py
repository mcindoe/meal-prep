from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any

import yaml

from mealprep.src.constants import MealProperty, MealTag, Unit
from mealprep.src.ingredient import (
    IngredientQuantity,
    get_ingredient_from_name,
)
from mealprep.src.meal import Meal


class RecipeError(BaseException):
    pass


class _RecipeEntry(Enum):
    NAME = "Name", True
    INGREDIENTS = "Ingredients", True
    PROPERTIES = "Properties", True
    TAGS = "Tags", False

    def __init__(self, entry_name: str, required: bool):
        self.entry_name = entry_name
        self.required = required


_REQUIRED_RECIPE_ENTRIES = set(x.entry_name for x in _RecipeEntry if x.required)
_UNITS_WITH_ABBREVIATIONS = tuple(unit for unit in Unit if unit.abbreviation is not None)


def _assert_recipe_validity(meal_contents: dict) -> None:
    missing_required_recipe_entries = _REQUIRED_RECIPE_ENTRIES - set(meal_contents.keys())
    if missing_required_recipe_entries:
        error_message = f"The following required entries are missing: {sorted(missing_required_recipe_entries)}"
        raise RecipeError(error_message)


def _parse_unit_quantity_description(description: str | int) -> tuple[Unit, int]:
    if isinstance(description, int):
        return (Unit.NUMBER, description)

    for unit in _UNITS_WITH_ABBREVIATIONS:
        if description.endswith(unit.abbreviation):
            try:
                return (unit, int(description.rstrip(unit.abbreviation)))
            except ValueError as exc:
                raise RecipeError(f"Unable to parse unit quantity {description}") from exc

    raise RecipeError(f"Unable to parse unit quantity description {description}")


def _get_key_and_value(entry: dict[str, str | int]) -> tuple[str, str | int]:
    return tuple(entry.items())[0]


def _parse_ingredient_entry(entry: str | dict[str, str | int]) -> IngredientQuantity:
    if isinstance(entry, dict):
        ingredient_name, quantity_description = _get_key_and_value(entry)
        unit, quantity = _parse_unit_quantity_description(quantity_description)

        return IngredientQuantity(ingredient=get_ingredient_from_name(ingredient_name), unit=unit, quantity=quantity)

    return IngredientQuantity(ingredient=get_ingredient_from_name(entry), unit=Unit.BOOL, quantity=True)


def _parse_property_entry(entry: dict[str, str]) -> tuple[MealProperty, Any]:
    property_name_component, property_value_component = _get_key_and_value(entry)

    try:
        meal_property = MealProperty[property_name_component.strip().upper()]
    except KeyError as exc:
        raise RecipeError(f"Unable to parse {property_name_component} as a MealProperty") from exc

    supported_values = meal_property.supported_values
    try:
        property_value = supported_values[property_value_component.strip().upper()]
    except KeyError as exc:
        raise RecipeError(f"Unable to parse {property_value_component} as a property of type {meal_property}") from exc

    print("Returning:")
    print(meal_property, property_value)

    return meal_property, property_value


def _parse_tag_entry(entry: str) -> MealTag:
    try:
        return MealTag[entry.strip().upper()]
    except KeyError as exc:
        raise RecipeError(f"Unable to parse {entry} as a MealTag instance") from exc


def parse_recipe_as_meal(recipe_filepath: Path) -> Meal:
    with open(recipe_filepath, "r", encoding="utf-8") as fp:
        recipe_contents = yaml.safe_load(fp)

    _assert_recipe_validity(recipe_contents)

    meal_name = recipe_contents[_RecipeEntry.NAME.entry_name]
    meal_ingredient_quantities = tuple(
        _parse_ingredient_entry(x) for x in recipe_contents[_RecipeEntry.INGREDIENTS.entry_name]
    )
    meal_properties = dict(tuple(_parse_property_entry(x) for x in recipe_contents[_RecipeEntry.PROPERTIES.entry_name]))

    if _RecipeEntry.TAGS.entry_name in recipe_contents:
        meal_tags = (_parse_tag_entry(x) for x in recipe_contents[_RecipeEntry.TAGS.entry_name])
    else:
        meal_tags = None

    return Meal(
        name=meal_name, ingredient_quantities=meal_ingredient_quantities, properties=meal_properties, tags=meal_tags
    )