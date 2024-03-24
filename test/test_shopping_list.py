import unittest

from mealprep.constants import Unit
from mealprep.ingredient import IngredientQuantity, Ingredients
from mealprep.meal import MealCollection
from mealprep.shopping_list import ShoppingList


class TestShoppingList(unittest.TestCase):
    shopping_list = ShoppingList(MealCollection())

    def test_get_ingredient_quantity_description(self):
        pear_ingredient_quantities = (
            IngredientQuantity(Ingredients.PEAR, Unit.BOOL, True),
            IngredientQuantity(Ingredients.PEAR, Unit.NUMBER, 2),
        )
        self.assertEqual(
            self.shopping_list.get_ingredient_quantity_description(pear_ingredient_quantities),
            "2 units plus some extra",
        )

        potato_ingredient_quantities = (IngredientQuantity(Ingredients.POTATO, Unit.BOOL, True),)
        self.assertIsNone(
            self.shopping_list.get_ingredient_quantity_description(potato_ingredient_quantities)
        )
