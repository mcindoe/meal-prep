from __future__ import annotations

from pathlib import Path

import yaml

from mealprep.src.constants import MealProperty, MealTag, Unit
from mealprep.src.ingredient import IngredientQuantity
from mealprep.src.meal import Meal
from mealprep.src.recipe.common import RecipeEntry


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
        RecipeEntry.NAME: meal.name,
        RecipeEntry.INGREDIENTS: meal_ingredients,
        RecipeEntry.PROPERTIES: meal_properties,
    }

    if meal_tags:
        meal_contents[RecipeEntry.TAGS] = meal_tags

    with open(recipe_filepath, "w", encoding="utf-8") as fp:
        for idx, (recipe_entry, entry_contents) in enumerate(
            sorted(meal_contents.items(), key=lambda x: x[0].recipe_index)
        ):
            written_entry = {recipe_entry.entry_name: entry_contents}
            fp.write(yaml.dump([written_entry]))

            if idx != len(meal_contents) - 1:
                fp.write("\n")


def _get_recipe_entry_from_ingredient_quantity(ingredient_quantity: IngredientQuantity) -> str | dict[str, int | str]:
    """
    Return a representation of the ingredient quantity which the yaml writer will
    write to file in a way which matches how a human would input this ingredient
    quantity into a recipe.

    NB: The awkward return type is that strings come with unwanted quote marks if
    they include "a: b" syntax etc.

    Examples Outputs:
        {"Beef Mince": "500g"} --> Beef Mince: 500g
        "Olive Oil" -> Olive Oil
        {"Pasta": "1 bag"} --> Pasta: 1 bag
        {"Peppers": 2} -> Peppers: 2
        {"Chopped Tomatoes": "2 jars"} -> Chopped Tomatoes: 2 jars
    """

    # TODO: Raise a PR / issue to correct the confusion between Ingredients instances and Ingredient instances,
    # and then this line should just read ingredient_quantity.ingredient.name
    ingredient_name = ingredient_quantity.ingredient.value.name

    if ingredient_quantity.unit == Unit.BOOL:
        return ingredient_name

    quantity = ingredient_quantity.quantity

    if ingredient_quantity.unit == Unit.NUMBER:
        return {ingredient_name: quantity}

    if quantity == 1:
        quantity_description = f"{quantity} {ingredient_quantity.unit.singular}"
    else:
        abbreviation = ingredient_quantity.unit.abbreviation
        if abbreviation is not None:
            quantity_description = f"{quantity}{abbreviation}"
        else:
            quantity_description = f"{quantity} {ingredient_quantity.unit.plural}"

    return {ingredient_name: quantity_description}
