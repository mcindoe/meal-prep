from mealprep.src.constants import Unit
from mealprep.src.ingredient import Ingredients
from mealprep.src.ingredient import IngredientQuantity
from mealprep.src.ingredient import IngredientQuantityCollection


class TestIngredientQuantityCollection:
    def test_initialiser(self):
        ingredient_quantities = (
            IngredientQuantity(Ingredients.BABY_SPINACH, Unit.BOOL, True),
            IngredientQuantity(Ingredients.CHERRY_TOMATO, Unit.NUMBER, 3),
            IngredientQuantity(Ingredients.CREAM, Unit.GRAM, 100),
        )
        x = IngredientQuantityCollection(ingredient_quantities)

        # IngredientQuantityCollections should maintain their own copy of the
        # ingredient quantities
        assert x.ingredient_quantities is not ingredient_quantities
