import unittest

from mealprep.constants import Category, Unit
from mealprep.ingredient import (
    Ingredient,
    IngredientQuantity,
    IngredientQuantityCollection,
    Ingredients,
)


class TestIngredient(unittest.TestCase):
    def test_initialiser(self):
        # Ingredient name is not a string
        with self.assertRaises(TypeError):
            Ingredient(3.5, Category.DAIRY)

        # Ingredient category is not an element of the Category enum
        with self.assertRaises(TypeError):
            Ingredient("Ingredient Name", "VEGETABLE")

    def test_getters(self):
        x = Ingredient("Baby Spinach", Category.VEGETABLE)
        self.assertEqual(x.name, "Baby Spinach")
        self.assertIs(x.category, Category.VEGETABLE)


class TestIngredientQuantity(unittest.TestCase):
    quantities = (
        IngredientQuantity(Ingredients.CREAM, Unit.MILLILITRE, 250),
        IngredientQuantity(Ingredients.PEAR, Unit.BOOL, True),
        IngredientQuantity(Ingredients.PEAR, Unit.NUMBER, 2),
    )

    def test_initialiser(self):
        # Ingredient argument is not an Ingredient
        with self.assertRaises(TypeError):
            IngredientQuantity("BAY LEAVES", Unit.BOOL, True)

        # Unit argument is not a Unit
        with self.assertRaises(TypeError):
            IngredientQuantity(Ingredients.BAY_LEAVES, "BOOL", True)

        # Boolean IngredientQuantity must have quantity = True
        with self.assertRaises(TypeError):
            IngredientQuantity(Ingredients.BAY_LEAVES, Unit.BOOL, False)

    def test_getters(self):
        x = IngredientQuantity(Ingredients.BAY_LEAVES, Unit.BOOL, True)
        self.assertIs(x.ingredient, Ingredients.BAY_LEAVES)
        self.assertIs(x.unit, Unit.BOOL)
        self.assertIs(x.quantity, True)

    def test_add(self):
        self.assertEqual(
            self.quantities[0] + self.quantities[0],
            IngredientQuantity(Ingredients.CREAM, Unit.MILLILITRE, 500),
        )
        self.assertEqual(
            self.quantities[1] + self.quantities[1],
            IngredientQuantity(Ingredients.PEAR, Unit.BOOL, True),
        )

        with self.assertRaises(TypeError):
            self.quantities[0] + self.quantities[1]

        with self.assertRaises(TypeError):
            self.quantities[1] + self.quantities[2]

    def test_eq(self):
        for n in range(3):
            self.assertEqual(self.quantities[n], self.quantities[n])

        self.assertNotEqual(self.quantities[0], self.quantities[1])
        self.assertNotEqual(self.quantities[0], self.quantities[2])
        self.assertNotEqual(self.quantities[1], self.quantities[2])


class TestIngredientQuantityCollection(unittest.TestCase):
    def test_initialiser(self):
        ingredient_quantities = (
            IngredientQuantity(Ingredients.BABY_SPINACH, Unit.BOOL, True),
            IngredientQuantity(Ingredients.CHERRY_TOMATOES, Unit.NUMBER, 3),
            IngredientQuantity(Ingredients.CREAM, Unit.GRAM, 100),
        )
        x = IngredientQuantityCollection(ingredient_quantities)

        # IngredientQuantityCollections should maintain their own copy of the
        # ingredient self.quantities
        self.assertIsNot(x.ingredient_quantities, ingredient_quantities)

        with self.assertRaises(TypeError):
            # One of the arguments is not an IngredientQuantity
            IngredientQuantityCollection(
                ingredient_quantities[:2] + (Ingredients.CREAM, Unit.GRAM, 100)
            )
