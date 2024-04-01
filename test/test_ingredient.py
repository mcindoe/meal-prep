import unittest

from mealprep.constants import Category, Unit
from mealprep.ingredient import Ingredient, IngredientQuantity, IngredientQuantityCollection


class TestIngredient(unittest.TestCase):
    def test_initialiser(self):
        # Ingredient name is not a string
        with self.assertRaises(TypeError):
            Ingredient(3.5, Category.DAIRY)

        # Ingredient category argument is not a Category instance
        with self.assertRaises(TypeError):
            Ingredient("Ingredient Name", "VEGETABLE")

    def test_getters(self):
        x = Ingredient("Baby Spinach", Category.VEGETABLE)
        self.assertEqual(x.name, "Baby Spinach")
        self.assertIs(x.category, Category.VEGETABLE)

    def test_initialise_from_name(self):
        x = Ingredient.from_name("Baby Spinach")
        self.assertEqual(x.name, "Baby Spinach")
        self.assertIs(x.category, Category.VEGETABLE)


class TestIngredientQuantity(unittest.TestCase):
    quantities = (
        IngredientQuantity(Ingredient.from_name("Cream"), Unit.MILLILITRE, 250),
        IngredientQuantity(Ingredient.from_name("Pear"), Unit.BOOL, True),
        IngredientQuantity(Ingredient.from_name("Pear"), Unit.NUMBER, 2),
    )

    def test_initialiser(self):
        # Ingredient argument is not an Ingredient
        with self.assertRaises(TypeError):
            IngredientQuantity("BAY LEAVES", Unit.BOOL, True)

        # Unit argument is not a Unit
        with self.assertRaises(TypeError):
            IngredientQuantity(Ingredient.from_name("Bay Leaves"), "BOOL", True)

        # Boolean IngredientQuantity must have quantity = True
        with self.assertRaises(TypeError):
            IngredientQuantity(Ingredient.from_name("Bay Leaves"), Unit.BOOL, False)

    def test_getters(self):
        x = IngredientQuantity(Ingredient.from_name("Bay Leaves"), Unit.BOOL, True)
        self.assertEqual(x.ingredient, Ingredient.from_name("Bay Leaves"))
        self.assertEqual(x.unit, Unit.BOOL)
        self.assertIs(x.quantity, True)

    def test_add(self):
        self.assertEqual(
            self.quantities[0] + self.quantities[0],
            IngredientQuantity(Ingredient.from_name("Cream"), Unit.MILLILITRE, 500),
        )
        self.assertEqual(
            self.quantities[1] + self.quantities[1],
            IngredientQuantity(Ingredient.from_name("Pear"), Unit.BOOL, True),
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
            IngredientQuantity(Ingredient.from_name("Baby Spinach"), Unit.BOOL, True),
            IngredientQuantity(Ingredient.from_name("Cherry Tomatoes"), Unit.NUMBER, 3),
            IngredientQuantity(Ingredient.from_name("Cream"), Unit.GRAM, 100),
        )
        x = IngredientQuantityCollection(ingredient_quantities)

        # IngredientQuantityCollections should maintain their own copy of the
        # ingredient self.quantities
        self.assertIsNot(x.ingredient_quantities, ingredient_quantities)

        with self.assertRaises(TypeError):
            # One of the arguments is not an IngredientQuantity
            IngredientQuantityCollection(
                ingredient_quantities[:2] + (Ingredient.from_name("Cream"), Unit.GRAM, 100)
            )
