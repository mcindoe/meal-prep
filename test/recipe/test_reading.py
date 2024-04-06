from __future__ import annotations

import unittest

from mealprep.constants import MealMeat, MealProperty, MealTag, Unit
from mealprep.ingredient import Ingredient, IngredientQuantity, IngredientQuantityCollection
from mealprep.loc import ROOT_DIR
from mealprep.meal import Meal
from mealprep.recipe.common import RecipeError
from mealprep.recipe.reading import (
    _parse_ingredient_quantity_from_recipe_entry,
    _parse_meal_property_entry,
    _parse_meal_tag_entry,
    _parse_unit_quantity_description,
    parse_recipe_as_meal,
)


TEST_RESOURCES_DIR = ROOT_DIR / "test/resources"


class TestRecipeParser(unittest.TestCase):
    def test_parse_unit_quantity_description(self):
        test_cases = (
            ("250g", (Unit.GRAM, 250)),
            (42, (Unit.NUMBER, 42)),
            ("10ml", (Unit.MILLILITRE, 10)),
            ("7 bags", (Unit.BAG, 7)),
        )

        for entry, expected in test_cases:
            self.assertEqual(_parse_unit_quantity_description(entry), expected)

    def test_parse_ingredient_quantity_from_recipe_entry(self):
        test_cases = (
            (
                {"Carrot": "50g"},
                IngredientQuantity(Ingredient.from_name("Carrot"), Unit.GRAM, 50),
            ),
            (
                {"Flour": "2 bags"},
                IngredientQuantity(Ingredient.from_name("Flour"), Unit.BAG, 2),
            ),
            (
                "Bay Leaves",
                IngredientQuantity(Ingredient.from_name("Bay Leaves"), Unit.BOOL, True),
            ),
            (
                {"Chicken Breast": 2},
                IngredientQuantity(Ingredient.from_name("Chicken Breast"), Unit.NUMBER, 2),
            ),
        )

        for entry, expected in test_cases:
            self.assertEqual(_parse_ingredient_quantity_from_recipe_entry(entry), expected)

    def test_parse_meal_property_entry(self):
        test_cases = (
            ({"Meat": "Beef"}, (MealProperty.MEAT, MealMeat.BEEF)),
            ({"Meat": "Chicken"}, (MealProperty.MEAT, MealMeat.CHICKEN)),
            ({"meat": "CHICKEN"}, (MealProperty.MEAT, MealMeat.CHICKEN)),
        )

        for entry, expected in test_cases:
            self.assertEqual(_parse_meal_property_entry(entry), expected)

        with self.assertRaises(RecipeError):
            _parse_meal_property_entry({"Foo": "Bar"})

        with self.assertRaises(RecipeError):
            _parse_meal_property_entry({"Meat": "Foo"})

    def test_parse_meal_tag_entry(self):
        test_cases = (
            ("INDIAN", MealTag.INDIAN),
            ("roast", MealTag.ROAST),
            ("vegetarian", MealTag.VEGETARIAN),
        )

        for entry, expected in test_cases:
            self.assertEqual(_parse_meal_tag_entry(entry), expected)

    def test_parse_recipe_as_meal(self):
        beef_and_ale_stew_file_path = TEST_RESOURCES_DIR / "test_recipe.yaml"
        meal = parse_recipe_as_meal(beef_and_ale_stew_file_path)

        expected_meal = Meal(
            name="Test Meal",
            ingredient_quantities=IngredientQuantityCollection(
                (
                    IngredientQuantity(Ingredient.from_name("Bay Leaves"), Unit.BOOL, True),
                    IngredientQuantity(Ingredient.from_name("Carrot"), Unit.NUMBER, 2),
                    IngredientQuantity(Ingredient.from_name("Celery"), Unit.NUMBER, 2),
                    IngredientQuantity(Ingredient.from_name("Chopped Tomatoes"), Unit.NUMBER, 1),
                    IngredientQuantity(Ingredient.from_name("Flour"), Unit.BOOL, True),
                    IngredientQuantity(Ingredient.from_name("Guinness"), Unit.MILLILITRE, 500),
                    IngredientQuantity(Ingredient.from_name("Onion"), Unit.NUMBER, 2),
                    IngredientQuantity(Ingredient.from_name("Potato"), Unit.GRAM, 900),
                    IngredientQuantity(Ingredient.from_name("Stewing Beef"), Unit.GRAM, 750),
                )
            ),
            properties={
                MealProperty.MEAT: MealMeat.BEEF,
            },
            tags=(MealTag.WINTER,),
        )

        self.assertEqual(meal.name, expected_meal.name)
        self.assertEqual(meal.ingredient_quantities, expected_meal.ingredient_quantities)
        self.assertEqual(meal.metadata, expected_meal.metadata)
