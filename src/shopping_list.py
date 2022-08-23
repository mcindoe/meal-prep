"""
Notes:

Purpose of the class is to provide a neat interface to recording and writing
ingredients required for a collection 

Some sort of grouping is required:
	- I want to group ingredients together:
		- If we have two IngredientQuantities of the same Ingredient and Unit, they can be directly summed
		- Otherwise, I'm going to keep them separate
		- It's important to retain the ingredients from which each ingredient collection is composed,
			since I'm going to display it in the final output
"""

import datetime as dt
from pathlib import Path
from typing import Iterable
from typing import Union

from mealprep.src.constants import Category
from mealprep.src.constants import Unit
from mealprep.src.ingredient import IngredientQuantity
from mealprep.src.meal import MealCollection


class ShoppingList:
	DATE_FORMAT_FOR_FILENAME = "%Y%m%d"

	@staticmethod
	def get_filename(start_date: dt.date, end_date: dt.date):
		start_date_str = start_date.strftime(ShoppingList.DATE_FORMAT_FOR_FILENAME)
		end_date_str = end_date.strftime(ShoppingList.DATE_FORMAT_FOR_FILENAME)

		return f"shopping_list_{start_date_str}_{end_date_str}.txt"

	def __init__(self, meal_collection: MealCollection):
		"""
		Parse the passed meal_collection into the following tree structure

		Category -> Ingredient -> Meals
							   -> Units -> IngredientQuantity

		Ingredient nodes point to the meals which contribute some of that
		Ingredient, and the total IngredientQuantities in each represented
		unit
		"""

		if not isinstance(meal_collection, MealCollection):
			raise TypeError(
				"Error in ShoppingList init: 'meal_collection' argument must be a MealCollection"\
			)

		self.ingredient_summary = {}

		for meal in meal_collection.meals:
			for ingredient_quantity in meal.ingredient_quantities.ingredient_quantities:
				ingredient = ingredient_quantity.ingredient
				category = ingredient.value.category
				unit = ingredient_quantity.unit

				if category not in self.ingredient_summary:
					self.ingredient_summary[category] = {}

				if ingredient not in self.ingredient_summary[category]:
					self.ingredient_summary[category][ingredient] = {
						"meals": MealCollection(),
						"quantities": {}
					}

				self.ingredient_summary[category][ingredient]["meals"] = (
					self.ingredient_summary[category][ingredient]["meals"].append(meal)
				)

				if unit in self.ingredient_summary[category][ingredient]["quantities"]:
					self.ingredient_summary[category][ingredient]["quantities"][unit] += ingredient_quantity
				else:
					self.ingredient_summary[category][ingredient]["quantities"][unit] = ingredient_quantity

	@staticmethod
	def get_ingredient_quantity_description(ingredient_quantities: Iterable[IngredientQuantity]) -> Union[str, None]:
		"""
		Get a human-readable description of the quantities required of a
		given ingredient to be included in a shopping list. E.g.

		((Ingredients.APPLE, Unit.BOOL, True),
			(Ingredients.APPLE, Unit.NUMBER, 2)) -> "2 units and some extra"

		((Ingredients.BANANA, Unit.BOOL, True)) -> None
		"""

		if not all(isinstance(x, IngredientQuantity) for x in ingredient_quantities):
			raise TypeError("Entries passed in ingredient_quantities must be IngredientQuantities")

		ingredient_quantities = sorted(ingredient_quantities, key = lambda x: x.unit.order)

		bool_entry = any(x.unit == Unit.BOOL for x in ingredient_quantities)

		# If there is only one entry, and it's a BOOL, there's no message to display
		if len(ingredient_quantities) == 1 and bool_entry:
			return

		non_bool_quantities = tuple(x for x in ingredient_quantities if x.unit != Unit.BOOL)

		quantity_descriptions = [
			f"{x.quantity} {x.unit.singular if x.quantity == 1 else x.unit.plural}"
			for x in non_bool_quantities
		]

		ingredient_quantity_description = ", ".join(quantity_descriptions)

		if bool_entry:
			ingredient_quantity_description += " plus some extra"

		return ingredient_quantity_description


	def to_file(self, filepath: Path):
		if isinstance(filepath, str):
			filepath = Path(filepath)

		if not filepath.parent.exists():
			raise ValueError(
				"Error in ShoppingList.to_file: The specified filepath's parent does not exist"
			)

		with open(filepath, "w+") as fp:
			fp.write("Shopping List")

			categories = sorted(self.ingredient_summary.keys(), key = lambda x: x.order)

			for category in categories:
				fp.write(f"\n\n--- {category.name} ---\n")

				category_ingredients = sorted(
					self.ingredient_summary[category].keys(),
					key = lambda x: x.name
				)

				for ingredient in category_ingredients:
					quantities = self.ingredient_summary[category][ingredient]["quantities"].values()
					meals = self.ingredient_summary[category][ingredient]["meals"]

					ingredient_entry = f"- [ ] {ingredient.name}"

					ingredient_quantity_description = self.get_ingredient_quantity_description(quantities)
					if ingredient_quantity_description:
						ingredient_entry += f" - {ingredient_quantity_description}"

					fp.write(f"{ingredient_entry}\n")

					ingredient_meals_entry = ", ".join(meal.name for meal in meals.meals)
					fp.write(f"\t{ingredient_meals_entry}\n")
