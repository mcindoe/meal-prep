from typing import Any
from typing import Iterable

from mealprep.src.ingredient import Ingredient
from mealprep.src.constants import Unit


class IngredientQuantity:
    def __init__(self, ingredient: Ingredient, unit: Unit, quantity: Any):
        assert isinstance(ingredient, Ingredient)
        assert isinstance(unit, Unit)

        self.ingredient = ingredient
        self.unit = unit
        self.quantity = quantity


class IngredientQuantityCollection:
    def __init__(self, ingredient_quantities: Iterable[IngredientQuantity]):
        self.ingredient_quantities = tuple(x for x in ingredient_quantities)
