from collections.abc import Collection
from pathlib import Path
from typing import Any
from collections.abc import Callable

import pytest
from mealprep.src.constants import MealMeat, MealProperty, MealTag, Unit
from mealprep.src.ingredient import (
    IngredientQuantity,
    Ingredients,
    get_ingredient_from_name,
)
from mealprep.src.meal import Meal

HYPHEN_SPACE = "- "


class RecipeError(BaseException):
    pass


class RecipeParser:
    UNITS_WITH_ABBREVIATIONS = tuple(unit for unit in Unit if unit.abbreviation is not None)

    @staticmethod
    def _trim_entry_start(entry: str) -> str:
        if not entry.startswith(HYPHEN_SPACE):
            raise ValueError(f"Expected entry to start with '{HYPHEN_SPACE}'; got {entry}")
        return entry.lstrip(HYPHEN_SPACE)

    @classmethod
    def _parse_unit_quantity_description(cls, description: str) -> tuple[Unit, int]:
        for unit in cls.UNITS_WITH_ABBREVIATIONS:
            if description.endswith(unit.abbreviation):
                try:
                    return (unit, int(description.rstrip(unit.abbreviation)))
                except ValueError as exc:
                    raise ValueError(f"Unable to parse unit quantity {description}") from exc

        return (Unit.NUMBER, int(description))

    @classmethod
    def _parse_ingredient_entry(cls, entry: str) -> IngredientQuantity:
        entry = cls._trim_entry_start(entry)

        if ":" in entry:
            ingredient_name, quantity_description = entry.split(":")
            unit, quantity = cls._parse_unit_quantity_description(quantity_description)

            return IngredientQuantity(
                ingredient=get_ingredient_from_name(ingredient_name), unit=unit, quantity=quantity
            )

        return IngredientQuantity(ingredient=get_ingredient_from_name(entry), unit=Unit.BOOL, quantity=True)

    @classmethod
    def _parse_property_entry(cls, entry) -> tuple[MealProperty, Any]:
        entry = cls._trim_entry_start(entry)
        property_name_component, property_value_component = entry.split("=")

        try:
            meal_property = MealProperty[property_name_component.strip().upper()]
        except KeyError as exc:
            raise ValueError(f"Unable to parse {property_name_component} as a MealProperty") from exc

        supported_values = meal_property.supported_values
        try:
            property_value = supported_values[property_value_component.strip().upper()]
        except KeyError as exc:
            raise ValueError(
                f"Unable to parse {property_value_component} as a property of type {meal_property}"
            ) from exc

        return meal_property, property_value

    @classmethod
    def _parse_tag_entry(cls, entry) -> MealTag:
        entry = cls._trim_entry_start(entry)
        try:
            return MealTag[entry.strip().upper()]
        except KeyError as exc:
            raise ValueError(f"Unable to parse {entry} as a MealTag instance") from exc

    @classmethod
    def _parse_recipe_section(
        cls, recipe_lines: Collection[str], section_header_declaration: str, parse_section_entry: Callable
    ) -> list[Any]:
        section_header_declarations = [
            (line_index, entry)
            for line_index, entry in enumerate(recipe_lines)
            if entry.lower().startswith(section_header_declaration.lower())
        ]

        if not section_header_declarations:
            return []

        if len(section_header_declarations) > 1:
            raise RecipeError(f"Found multiple lines starting with '{section_header_declaration}'")

        section_contents = []
        line_index = section_header_declarations[0][0] + 1
        while (line_index < len(recipe_lines)) and (recipe_lines[line_index] != ""):
            section_entry = recipe_lines[line_index]
            section_contents.append(parse_section_entry(section_entry))
            line_index += 1

        return section_contents

    @classmethod
    def _parse_recipe_properties(cls, recipe_lines: Collection[str]) -> dict[MealProperty, Any]:
        properties_section_contents = cls._parse_recipe_section(
            recipe_lines, section_header_declaration="properties:", parse_section_entry=cls._parse_property_entry
        )

        return dict(properties_section_contents)

    @classmethod
    def _parse_recipe_tags(cls, recipe_lines: Collection[str]) -> list[MealTag]:
        return cls._parse_recipe_section(
            recipe_lines, section_header_declaration="tags:", parse_section_entry=cls._parse_tag_entry
        )

    @classmethod
    def parse(cls, recipe_filepath: Path) -> Meal:
        with open(recipe_filepath, "r", encoding="utf-8") as fp:
            recipe_lines = tuple(line.strip() for line in fp)

        meal_name = recipe_lines[0]

        if recipe_lines[1] != "":
            raise RecipeError(f"Expected a blank space after the recipe name in {recipe_filepath}")

        line_index = 2
        ingredient_quantities = []
        while recipe_lines[line_index] != "":
            ingredient_quantities.append(cls._parse_ingredient_entry(recipe_lines[line_index]))
            line_index += 1

        while recipe_lines[line_index] == "":
            line_index += 1

        ingredient_properties = []
        if recipe_lines[line_index].startswith("Properties:"):
            line_index += 1
            while recipe_lines[line_index] != "":
                ingredient_properties.append(cls._parse_property_entry(recipe_lines[line_index]))
                line_index += 1

        while recipe_lines[line_index] != "":
            line_index += 1

        print(recipe_lines)

        print("Ingredient quantities:")
        print(ingredient_quantities)


class TestRecipeParser:
    @pytest.fixture
    def parser(self) -> RecipeParser:
        return RecipeParser()

    def test_parse_unit_quantity_description(self, parser: RecipeParser):
        test_cases = (
            ("250g", (Unit.GRAM, 250)),
            ("42", (Unit.NUMBER, 42)),
            ("10ml", (Unit.MILLILITRE, 10)),
            ("7 bags", (Unit.BAG, 7)),
        )

        for entry, expected in test_cases:
            assert parser._parse_unit_quantity_description(entry) == expected

    def test_parse_ingredient_entry(self, parser: RecipeParser):
        test_cases = (
            (
                "- Carrot: 50g",
                IngredientQuantity(Ingredients.CARROT, Unit.GRAM, 50),
            ),
            (
                "- Flour: 2 bags",
                IngredientQuantity(Ingredients.FLOUR, Unit.BAG, 2),
            ),
            (
                "- Bay Leaves",
                IngredientQuantity(Ingredients.BAY_LEAVES, Unit.BOOL, True),
            ),
            (
                "- Chicken Breast: 2",
                IngredientQuantity(Ingredients.CHICKEN_BREAST, Unit.NUMBER, 2),
            ),
        )

        for entry, expected in test_cases:
            assert parser._parse_ingredient_entry(entry) == expected

    def test_parse_property_entry(self, parser: RecipeParser):
        test_cases = (
            ("- Meat = Beef", (MealProperty.MEAT, MealMeat.BEEF)),
            ("- Meat = Chicken", (MealProperty.MEAT, MealMeat.CHICKEN)),
            ("- meat=    CHICKEN", (MealProperty.MEAT, MealMeat.CHICKEN)),
        )

        for entry, expected in test_cases:
            assert parser._parse_property_entry(entry) == expected

        with pytest.raises(ValueError):
            parser._parse_property_entry("- Foo = Bar")

        with pytest.raises(ValueError):
            parser._parse_property_entry("- Meat = Foo")

    def test_parse_meal_tag_entry(self, parser: RecipeParser):
        test_cases = (
            ("- INDIAN", MealTag.INDIAN),
            ("- roast", MealTag.ROAST),
            ("-    vegetarian", MealTag.VEGETARIAN),
        )

        for entry, expected in test_cases:
            assert parser._parse_tag_entry(entry) == expected

        with pytest.raises(ValueError):
            parser._parse_tag_entry("VEGETARIAN")
