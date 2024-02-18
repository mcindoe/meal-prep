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
    NAME = "Name", True, 0
    INGREDIENTS = "Ingredients", True, 1
    PROPERTIES = "Properties", True, 2
    TAGS = "Tags", False, 3

    def __init__(self, entry_name: str, required: bool, recipe_index: int):
        self.entry_name = entry_name
        self.required = required
        self.recipe_index = recipe_index


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


def _parse_ingredient_quantity_from_recipe_entry(entry: str | dict[str, str | int]) -> IngredientQuantity:
    if isinstance(entry, dict):
        ingredient_name, quantity_description = _get_key_and_value(entry)
        unit, quantity = _parse_unit_quantity_description(quantity_description)

        return IngredientQuantity(ingredient=get_ingredient_from_name(ingredient_name), unit=unit, quantity=quantity)

    return IngredientQuantity(ingredient=get_ingredient_from_name(entry), unit=Unit.BOOL, quantity=True)


def _get_recipe_entry_from_ingredient_quantity(ingredient_quantity: IngredientQuantity) -> str | dict[str, str | int]:
    # TODO: Does it have to be this difficult?
    ingredient_name = ingredient_quantity.ingredient.value.name

    if ingredient_quantity.unit == Unit.BOOL:
        return ingredient_name

    quantity_description = ingredient_quantity.quantity
    if ingredient_quantity.unit.abbreviation:
        quantity_description = f"{quantity_description}{ingredient_quantity.unit.abbreviation}"

    return {ingredient_name: quantity_description}


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

    return meal_property, property_value


def _parse_tag_entry(entry: str) -> MealTag:
    try:
        return MealTag[entry.strip().upper()]
    except KeyError as exc:
        raise RecipeError(f"Unable to parse {entry} as a MealTag instance") from exc


def parse_recipe_as_meal(recipe_filepath: Path) -> Meal:
    with open(recipe_filepath, "r", encoding="utf-8") as fp:
        recipe_contents_entries = yaml.safe_load(fp)

    recipe_contents = {}
    for x in recipe_contents_entries:
        recipe_contents |= x

    _assert_recipe_validity(recipe_contents)

    meal_name = recipe_contents[_RecipeEntry.NAME.entry_name]
    meal_ingredient_quantities = tuple(
        _parse_ingredient_quantity_from_recipe_entry(x) for x in recipe_contents[_RecipeEntry.INGREDIENTS.entry_name]
    )
    meal_properties = dict(tuple(_parse_property_entry(x) for x in recipe_contents[_RecipeEntry.PROPERTIES.entry_name]))

    if _RecipeEntry.TAGS.entry_name in recipe_contents:
        meal_tags = (_parse_tag_entry(x) for x in recipe_contents[_RecipeEntry.TAGS.entry_name])
    else:
        meal_tags = None

    return Meal(
        name=meal_name, ingredient_quantities=meal_ingredient_quantities, properties=meal_properties, tags=meal_tags
    )


def write_meal_as_recipe(meal: Meal, recipe_filepath: Path) -> None:
    meal_ingredients = [_get_recipe_entry_from_ingredient_quantity(x) for x in meal.ingredient_quantities]

    meal_properties = []
    meal_tags = []
    for key, value in meal.metadata.items():
        if isinstance(key, MealProperty):
            meal_properties.append({key.description: value.value})
        elif isinstance(key, MealTag):
            if value is True:
                meal_tags.append(key.value)
            elif value is not False:
                raise RuntimeError("Unexpected value")
        else:
            raise RuntimeError(f"Unsupported type {type(key)} in meal metadata")

    meal_contents = {
        _RecipeEntry.NAME: meal.name,
        _RecipeEntry.INGREDIENTS: meal_ingredients,
        _RecipeEntry.PROPERTIES: meal_properties,
    }

    if meal_tags:
        meal_contents[_RecipeEntry.TAGS] = meal_tags

    with open(recipe_filepath, "w", encoding="utf-8") as fp:
        for idx, (recipe_entry, entry_contents) in enumerate(
            sorted(meal_contents.items(), key=lambda x: x[0].recipe_index)
        ):
            written_entry = {recipe_entry.entry_name: entry_contents}
            fp.write(yaml.dump([written_entry]))

            if idx != len(meal_contents) - 1:
                fp.write("\n")
