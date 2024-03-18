from __future__ import annotations

import pytest

from mealprep.src.constants import MealMeat, MealProperty, MealTag, Unit
from mealprep.src.ingredient import IngredientQuantity, IngredientQuantityCollection, Ingredients
from mealprep.src.loc import ROOT_DIR
from mealprep.src.meal import Meal
from mealprep.src.recipe.common import RecipeError
from mealprep.src.recipe.reading import (
    _parse_ingredient_quantity_from_recipe_entry,
    _parse_meal_tag_entry,
    _parse_meal_property_entry,
    _parse_unit_quantity_description,
    parse_recipe_as_meal,
)


TEST_RESOURCES_DIR = ROOT_DIR / "test/resources"


# TODO: Mark the inconsistent type here as a GitHub issue. I'm confusing Ingredients and Ingredient
class TestRecipeParser:
    def test_parse_unit_quantity_description(self):
        test_cases = (
            ("250g", (Unit.GRAM, 250)),
            (42, (Unit.NUMBER, 42)),
            ("10ml", (Unit.MILLILITRE, 10)),
            ("7 bags", (Unit.BAG, 7)),
        )

        for entry, expected in test_cases:
            assert _parse_unit_quantity_description(entry) == expected

    def test_parse_ingredient_quantity_from_recipe_entry(self):
        test_cases = (
            (
                {"Carrot": "50g"},
                IngredientQuantity(Ingredients.CARROT, Unit.GRAM, 50),
            ),
            (
                {"Flour": "2 bags"},
                IngredientQuantity(Ingredients.FLOUR, Unit.BAG, 2),
            ),
            (
                "Bay Leaves",
                IngredientQuantity(Ingredients.BAY_LEAVES, Unit.BOOL, True),
            ),
            (
                {"Chicken Breast": 2},
                IngredientQuantity(Ingredients.CHICKEN_BREAST, Unit.NUMBER, 2),
            ),
        )

        for entry, expected in test_cases:
            assert _parse_ingredient_quantity_from_recipe_entry(entry) == expected

    def test_parse_meal_property_entry(self):
        test_cases = (
            ({"Meat": "Beef"}, (MealProperty.MEAT, MealMeat.BEEF)),
            ({"Meat": "Chicken"}, (MealProperty.MEAT, MealMeat.CHICKEN)),
            ({"meat": "CHICKEN"}, (MealProperty.MEAT, MealMeat.CHICKEN)),
        )

        for entry, expected in test_cases:
            assert _parse_meal_property_entry(entry) == expected

        with pytest.raises(RecipeError):
            _parse_meal_property_entry({"Foo": "Bar"})

        with pytest.raises(RecipeError):
            _parse_meal_property_entry({"Meat": "Foo"})

    def test_parse_meal_tag_entry(self):
        test_cases = (
            ("INDIAN", MealTag.INDIAN),
            ("roast", MealTag.ROAST),
            ("vegetarian", MealTag.VEGETARIAN),
        )

        for entry, expected in test_cases:
            assert _parse_meal_tag_entry(entry) == expected

    def test_parse_recipe_as_meal(self):
        beef_and_ale_stew_file_path = TEST_RESOURCES_DIR / "test_recipe.yaml"
        meal = parse_recipe_as_meal(beef_and_ale_stew_file_path)

        expected_meal = Meal(
            name="Test Meal",
            ingredient_quantities=IngredientQuantityCollection(
                (
                    IngredientQuantity(Ingredients.BAY_LEAVES, Unit.BOOL, True),
                    IngredientQuantity(Ingredients.CARROT, Unit.NUMBER, 2),
                    IngredientQuantity(Ingredients.CELERY, Unit.NUMBER, 2),
                    IngredientQuantity(Ingredients.CHOPPED_TOMATOES, Unit.NUMBER, 1),
                    IngredientQuantity(Ingredients.FLOUR, Unit.BOOL, True),
                    IngredientQuantity(Ingredients.GUINNESS, Unit.MILLILITRE, 500),
                    IngredientQuantity(Ingredients.ONION, Unit.NUMBER, 2),
                    IngredientQuantity(Ingredients.POTATO, Unit.GRAM, 900),
                    IngredientQuantity(Ingredients.STEWING_BEEF, Unit.GRAM, 750),
                )
            ),
            properties={
                MealProperty.MEAT: MealMeat.BEEF,
            },
            tags=(MealTag.WINTER,),
        )

        assert all(
            (
                meal.name == expected_meal.name,
                meal.ingredient_quantities == expected_meal.ingredient_quantities,
                meal.metadata == expected_meal.metadata,
            )
        )
