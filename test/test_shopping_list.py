import pytest

from mealprep.src.constants import Unit
from mealprep.src.ingredient import Ingredients
from mealprep.src.ingredient import IngredientQuantity
from mealprep.src.meal import MealCollection
from mealprep.src.shopping_list import ShoppingList


class TestShoppingList:
    @pytest.fixture()
    def shopping_list(self):
        return ShoppingList(MealCollection())

    def test_get_ingredient_quantity_description(self, shopping_list):
        pear_ingredient_quantities = (
            IngredientQuantity(Ingredients.PEAR, Unit.BOOL, True),
            IngredientQuantity(Ingredients.PEAR, Unit.NUMBER, 2),
        )
        assert shopping_list.get_ingredient_quantity_description(pear_ingredient_quantities) == (
            "2 units plus some extra"
        )

        potato_ingredient_quantities = (
            IngredientQuantity(Ingredients.POTATO, Unit.BOOL, True),
        )
        assert shopping_list.get_ingredient_quantity_description(potato_ingredient_quantities) is None
