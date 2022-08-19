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


from mealprep.src.meal import MealCollection


class ShoppingList:
	def __init__(self, meal_collection: MealCollection):
		if not isinstance(meal_collection, MealCollection):
			raise TypeError(
				"Error in ShoppingList init: 'meal_collection' argument must be a MealCollection"\
			)

		self.ingredient_summary = {}

		for meal in meal_collection.meals:
			for ingredient_quantity in meal.ingredient_quantities.ingredient_quantities:
				ingredient = ingredient_quantity.ingredient
				unit = ingredient_quantity.unit

				if ingredient not in self.ingredient_summary:
					self.ingredient_summary[ingredient] = {}

				if unit in self.ingredient_summary[ingredient]:
					self.ingredient_summary[ingredient][unit]["quantity"] += ingredient_quantity
					self.ingredient_summary[ingredient][unit]["meals"] = (
						self.ingredient_summary[ingredient][unit]["meals"].append(meal)
					)
				else:
					self.ingredient_summary[ingredient][unit] = {
						"quantity": ingredient_quantity,
						"meals": MealCollection((meal,))
					}