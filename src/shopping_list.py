import collections
import datetime as dt
from pathlib import Path
from typing import Iterable, Union

from mealprep.src.constants import Unit
from mealprep.src.ingredient import IngredientQuantity
from mealprep.src.meal import MealCollection


class ShoppingList:
    DATE_FORMAT_FOR_FILENAME = "%Y%m%d"

    @staticmethod
    def get_filename(start_date: dt.date, end_date: dt.date) -> str:
        start_date_str = start_date.strftime(ShoppingList.DATE_FORMAT_FOR_FILENAME)
        end_date_str = end_date.strftime(ShoppingList.DATE_FORMAT_FOR_FILENAME)

        return f"shopping_list_{start_date_str}_{end_date_str}.txt"

    def __init__(self, meal_collection: MealCollection):
        """
        Parse the passed meal_collection into the following tree structure

        Category -> Ingredient -> Meals
                               -> Units -> IngredientQuantity

        Ingredient nodes point to the meals which contribute some of that
        Ingredient, and the total IngredientQuantities in each
        represented unit
        """

        if not isinstance(meal_collection, MealCollection):
            raise TypeError("'meal_collection' argument must be a MealCollection")

        self.ingredient_summary = {}

        for meal in meal_collection:
            for ingredient_quantity in meal.ingredient_quantities:
                ingredient = ingredient_quantity.ingredient
                category = ingredient.value.category
                unit = ingredient_quantity.unit

                if category not in self.ingredient_summary:
                    self.ingredient_summary[category] = {}

                if ingredient not in self.ingredient_summary[category]:
                    self.ingredient_summary[category][ingredient] = {
                        "meals": MealCollection(),
                        "quantities": {},
                    }

                self.ingredient_summary[category][ingredient]["meals"] += meal

                if unit in self.ingredient_summary[category][ingredient]["quantities"]:
                    self.ingredient_summary[category][ingredient]["quantities"][
                        unit
                    ] += ingredient_quantity
                else:
                    self.ingredient_summary[category][ingredient]["quantities"][
                        unit
                    ] = ingredient_quantity

    @staticmethod
    def get_ingredient_quantity_description(
        ingredient_quantities: Iterable[IngredientQuantity],
    ) -> Union[str, None]:
        """
        Get a human-readable description of the quantities required of a
        given ingredient (to be included in a shopping list). Return None
        in the case of only boolean units, to avoid "PEAR - some" type
        entries

        Examples:

        (
            (Ingredients.PEAR, Unit.BOOL, True),
            (Ingredients.PEAR, Unit.NUMBER, 2)
        ) -> "2 units and some extra"

        ((Ingredients.BANANA, Unit.BOOL, True), ) -> None
        """

        if not all(isinstance(x, IngredientQuantity) for x in ingredient_quantities):
            raise TypeError("Entries passed in ingredient_quantities must be IngredientQuantities")

        if len(set(x.ingredient for x in ingredient_quantities)) != 1:
            raise ValueError("Multiple ingredients passed to get_ingredient_quantity_description")

        # There should be no more than one of each unit passed
        if max(collections.Counter(x.unit for x in ingredient_quantities).values()) != 1:
            raise ValueError(
                "Multiple entries passed for a unit in get_ingredient_quantity_description"
            )

        units = {x.unit for x in ingredient_quantities}

        # If there are only boolean entries, there's no message to display
        if units == {Unit.BOOL}:
            return

        ingredient_quantities = sorted(ingredient_quantities, key=lambda x: x.unit.order)
        non_bool_quantities = tuple(x for x in ingredient_quantities if x.unit is not Unit.BOOL)

        quantity_descriptions = [
            f"{x.quantity} {x.unit.singular if x.quantity == 1 else x.unit.plural}"
            for x in non_bool_quantities
        ]

        ingredient_quantity_description = ", ".join(quantity_descriptions)

        if Unit.BOOL in units:
            ingredient_quantity_description += " plus some extra"

        return ingredient_quantity_description

    def to_file(self, filepath: Union[Path, str]):
        if isinstance(filepath, str):
            filepath = Path(filepath)

        if not filepath.parent.exists():
            raise ValueError(
                "Error in ShoppingList.to_file: the specified filepath's parent does not exist"
            )

        with open(filepath, "w+") as fp:
            fp.write("Shopping List\n")

            categories = sorted(self.ingredient_summary.keys(), key=lambda x: x.order)

            for category in categories:
                fp.write(f"\n\n--- {category.list_header} ---\n")

                category_ingredients = sorted(
                    self.ingredient_summary[category].keys(), key=lambda x: x.name
                )

                for ingredient in category_ingredients:
                    quantities = self.ingredient_summary[category][ingredient][
                        "quantities"
                    ].values()
                    meals = self.ingredient_summary[category][ingredient]["meals"]

                    ingredient_entry = f"- [ ] {ingredient.value.name}"

                    ingredient_quantity_description = self.get_ingredient_quantity_description(
                        quantities
                    )
                    if ingredient_quantity_description is not None:
                        ingredient_entry += f": {ingredient_quantity_description}"

                    fp.write(f"{ingredient_entry}\n")

                    ingredient_meals_entry = ", ".join(meal.name for meal in meals)
                    fp.write(f"\t{ingredient_meals_entry}\n")
