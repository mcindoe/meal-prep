import re
from pathlib import Path
from typing import Any

import yaml

from mealprep.constants import MealProperty, MealTag, Unit, UNIT_IDENTIFIERS
from mealprep.ingredient import (
    Ingredient,
    IngredientQuantity,
    IngredientQuantityCollection,
)
from mealprep.meal import Meal
from mealprep.recipe.common import RecipeEntry, RecipeError


ALPHABETICAL_CHARACTER_REGEX = re.compile("[a-zA-Z]")
REQUIRED_RECIPE_ENTRIES = set(x.entry_name for x in RecipeEntry if x.required)


def parse_recipe_as_meal(recipe_filepath: Path) -> Meal:
    with open(recipe_filepath, "r", encoding="utf-8") as fp:
        recipe_contents_entries = yaml.safe_load(fp)

    recipe_contents = {}
    for x in recipe_contents_entries:
        recipe_contents |= x

    _assert_recipe_contains_required_fields(recipe_contents)

    meal_name = recipe_filepath.name.removesuffix(".yaml")
    meal_ingredient_quantities = tuple(
        _parse_ingredient_quantity_from_recipe_entry(x)
        for x in recipe_contents[RecipeEntry.INGREDIENTS.entry_name]
    )
    meal_properties = dict(
        tuple(
            _parse_meal_property_entry(x)
            for x in recipe_contents[RecipeEntry.PROPERTIES.entry_name]
        )
    )

    if RecipeEntry.TAGS.entry_name in recipe_contents:
        meal_tags = (_parse_meal_tag_entry(x) for x in recipe_contents[RecipeEntry.TAGS.entry_name])
    else:
        meal_tags = None

    return Meal(
        name=meal_name,
        ingredient_quantities=IngredientQuantityCollection(meal_ingredient_quantities),
        properties=meal_properties,
        tags=meal_tags,
    )


def _assert_recipe_contains_required_fields(recipe_contents: dict) -> None:
    """
    The expected argument format is that passed from the yaml parser. We
    check that all required fields are present in the read dictionary
    """

    missing_required_recipe_entries = REQUIRED_RECIPE_ENTRIES - set(recipe_contents.keys())
    if missing_required_recipe_entries:
        error_message = (
            f"The following required entries are missing: {sorted(missing_required_recipe_entries)}"
        )
        raise RecipeError(error_message)


def _parse_unit_quantity_description(description: str | int) -> tuple[Unit, int]:
    """
    Parse a representation of a unit quantity, as loaded from the yaml reader,
    into a (Unit, quantity) tuple. Since the input is from the yaml reader,
    values which can be parsed as integers are represented as integers, and
    otherwise we receive a string

    Examples:
        "7 bags" -> (Unit.BAG, 7)
        7 -> (Unit.NUMBER, 7)
        "100g" -> (Unit.GRAM, 100)
    """

    if isinstance(description, int):
        return Unit.NUMBER, description

    assert isinstance(description, str), f"Unsupported type {type(description)}"

    # Separate description into the left-hand numeric portion and right-hand unit identifier
    original_description = description
    description = description.replace(" ", "")
    first_alphabetical_character_index = ALPHABETICAL_CHARACTER_REGEX.search(description).start()
    numeric_portion = description[:first_alphabetical_character_index]
    unit_portion = description[first_alphabetical_character_index:]

    try:
        quantity_value = int(numeric_portion)
    except ValueError as exc:
        raise RecipeError(
            f"Unable to parse unit quantity {original_description} - can't parse {numeric_portion} as an integer"
        ) from exc

    for identifier, unit in UNIT_IDENTIFIERS.items():
        if unit_portion.endswith(identifier):
            return unit, quantity_value

    raise RecipeError(
        f"Unable to parse unit quantity description {original_description} - can't infer a unit from {unit_portion}"
    )


def _parse_ingredient_quantity_from_recipe_entry(
    entry: str | dict[str, str | int]
) -> IngredientQuantity:
    """
    Parse an ingredient quantity, as parsed by the yaml reader, to an
    IngredientQuantity instance. The mixed type inputs are in response
    to yaml parsing, for example, "7" as 7 (int), "Bacon: 300g" as
    {"Bacon": "300g"}, etc

    Example inputs:
        "Bacon" -> (Ingredient.from_name("Bacon"), Unit.BOOL, True)
        {"Bacon": "300g"} -> (Ingredient.from_name("Bacon"), Unit.GRAMS, 300)
        {"Bacon": 3} -> (Ingredient.from_name("Bacon"), Unit.NUMBER, 3)
    """

    if isinstance(entry, str):
        return IngredientQuantity(
            ingredient=Ingredient.from_name(entry), unit=Unit.BOOL, quantity=True
        )

    if isinstance(entry, dict):
        ingredient_name, quantity_description = tuple(entry.items())[0]
        unit, quantity = _parse_unit_quantity_description(quantity_description)

        return IngredientQuantity(
            ingredient=Ingredient.from_name(ingredient_name), unit=unit, quantity=quantity
        )

    raise TypeError(
        f"Unsupported type {type(entry)} passed to _parse_ingredient_quantity_from_recipe_entry"
    )


def _parse_meal_property_entry(entry: dict[str, str]) -> tuple[MealProperty, Any]:
    property_name_component, property_value_component = tuple(entry.items())[0]

    try:
        meal_property = MealProperty[property_name_component.strip().upper()]
    except KeyError as exc:
        raise RecipeError(f"Unable to parse {property_name_component} as a MealProperty") from exc

    supported_values = meal_property.supported_values
    try:
        property_value = supported_values[property_value_component.strip().upper()]
    except KeyError as exc:
        raise RecipeError(
            f"Unable to parse {property_value_component} as a property of type {meal_property}"
        ) from exc

    return meal_property, property_value


def _parse_meal_tag_entry(entry: str) -> MealTag:
    try:
        return MealTag[entry.strip().upper()]
    except KeyError as exc:
        raise RecipeError(f"Unable to parse {entry} as a MealTag") from exc
