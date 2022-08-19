import pytest

from mealprep.src.constants import Category
from mealprep.src.constants import Unit
from mealprep.src.ingredient import Ingredient
from mealprep.src.ingredient import Ingredients
from mealprep.src.ingredient import IngredientQuantity
from mealprep.src.ingredient import IngredientQuantityCollection


class TestIngredient:
    def test_initialiser(self):
        # Ingredient name is not a string
        with pytest.raises(TypeError):
            Ingredient(3.5, Category.DAIRY)

        # Ingredient category is not an element of the Category enum
        with pytest.raises(TypeError):
            Ingredient("Ingredient Name", "VEGETABLE")

    def test_getters(self):
        x = Ingredient("Baby Spinach", Category.VEGETABLE)
        assert x.name == "Baby Spinach"
        assert x.category is Category.VEGETABLE

# TODO: Need to test for types in IngredientQuantityCollection constructor


class TestIngredientQuantity:
    def test_initialiser(self):
        # Ingredient argument is not an Ingredient
        with pytest.raises(TypeError):
            IngredientQuantity("BAY LEAVES", Unit.BOOL, True)

        # Unit argument is not a Unit
        with pytest.raises(TypeError):
            IngredientQuantity(Ingredients.BAY_LEAVES, "BOOL", True)

    def test_getters(self):
        x = IngredientQuantity(Ingredients.BAY_LEAVES, Unit.BOOL, True)
        assert x.ingredient is Ingredients.BAY_LEAVES
        assert x.unit is Unit.BOOL
        assert x.quantity is True


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
