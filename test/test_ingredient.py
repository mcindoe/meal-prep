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


class TestIngredientQuantity:
    @pytest.fixture()
    def quantities(self):
        quantity1 = IngredientQuantity(Ingredients.CREAM, Unit.MILLILITRE, 250)
        quantity2 = IngredientQuantity(Ingredients.PEAR, Unit.BOOL, True)
        quantity3 = IngredientQuantity(Ingredients.PEAR, Unit.NUMBER, 2)

        yield quantity1, quantity2, quantity3

    def test_initialiser(self):
        # Ingredient argument is not an Ingredient
        with pytest.raises(TypeError):
            IngredientQuantity("BAY LEAVES", Unit.BOOL, True)

        # Unit argument is not a Unit
        with pytest.raises(TypeError):
            IngredientQuantity(Ingredients.BAY_LEAVES, "BOOL", True)

        # Boolean IngredientQuantity must have quantity = True
        with pytest.raises(TypeError):
            IngredientQuantity(Ingredients.BAY_LEAVES, Unit.BOOL, False)

    def test_getters(self):
        x = IngredientQuantity(Ingredients.BAY_LEAVES, Unit.BOOL, True)
        assert x.ingredient is Ingredients.BAY_LEAVES
        assert x.unit is Unit.BOOL
        assert x.quantity is True

    def test_add(self, quantities):
        assert quantities[0] + quantities[0] == IngredientQuantity(Ingredients.CREAM, Unit.MILLILITRE, 500)
        assert quantities[1] + quantities[1] == IngredientQuantity(Ingredients.PEAR, Unit.BOOL, True)

        with pytest.raises(TypeError):
            quantities[0] + quantities[1]

        with pytest.raises(TypeError):
            quantities[1] + quantities[2]

    def test_eq(self, quantities):
        assert quantities[0] == quantities[0]
        assert quantities[1] == quantities[1]
        assert quantities[2] == quantities[2]

        assert quantities[0] != quantities[1]
        assert quantities[0] != quantities[2]
        assert quantities[1] != quantities[2]


class TestIngredientQuantityCollection:
    def test_initialiser(self):
        ingredient_quantities = (
            IngredientQuantity(Ingredients.BABY_SPINACH, Unit.BOOL, True),
            IngredientQuantity(Ingredients.CHERRY_TOMATOES, Unit.NUMBER, 3),
            IngredientQuantity(Ingredients.CREAM, Unit.GRAM, 100),
        )
        x = IngredientQuantityCollection(ingredient_quantities)

        # IngredientQuantityCollections should maintain their own copy of the
        # ingredient quantities
        assert x.ingredient_quantities is not ingredient_quantities

        with pytest.raises(TypeError):
            # One of the arguments is not an IngredientQuantity
            IngredientQuantityCollection(
                ingredient_quantities[:2] + (Ingredients.CREAM, Unit.GRAM, 100)
            )
