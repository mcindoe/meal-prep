from typing import Iterable

from mealprep.src.constants import BaseEnum
from mealprep.src.constants import Category


class Ingredient:
    def __init__(self, name: str, category: Category):
        self.name = name
        self.category = category


class IngredientCollection:
    def __init__(self, ingredients: Iterable[Ingredient]):
        self.ingredients = tuple(x for x in ingredients)


class Ingredients(BaseEnum):
    CARROT = Ingredient("Carrot", Category.VEGETABLE)
    PEAR = Ingredient("Pear", Category.FRUIT)
