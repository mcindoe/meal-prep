import csv
from typing import Any, Iterable

from mealprep.basic_iterator import BasicIterator
from mealprep.constants import Category, Unit
from mealprep.loc import SUPPORTED_INGREDIENT_INFO_FILE


class Ingredient:
    _SUPPORTED_INGREDIENT_INFO: dict[str, dict[str, str]] = {}
    with open(SUPPORTED_INGREDIENT_INFO_FILE, "r") as fp:
        reader = csv.DictReader(fp)
        for ingredient_info in reader:
            _SUPPORTED_INGREDIENT_INFO[ingredient_info["name"]] = ingredient_info

    def __init__(self, name: str, category: Category):
        if not isinstance(name, str):
            raise TypeError("'name' argument must be a string in Ingredient init")
        if not isinstance(category, Category):
            raise TypeError("'category' argument must be a Category in Ingredient init")

        self.name = name
        self.category = category

    @staticmethod
    def from_name(ingredient_name: str) -> "Ingredient":
        try:
            ingredient_info = Ingredient._SUPPORTED_INGREDIENT_INFO[ingredient_name]
        except KeyError:
            raise ValueError(f"Unsupported ingredient name {ingredient_name}")

        return Ingredient(
            name=ingredient_info["name"], category=Category[ingredient_info["category"]]
        )

    def __eq__(self, other: "Ingredient") -> bool:
        return (self.name == other.name) and (self.category == other.category)

    def __hash__(self) -> int:
        return hash(f"Ingredient('{self.name}')")

    def __repr__(self) -> str:
        return f'Ingredient(name="{self.name}", category=Category.{self.category.name})'


class IngredientQuantity:
    def __init__(self, ingredient: Ingredient, unit: Unit, quantity: Any):
        if not isinstance(ingredient, Ingredient):
            raise TypeError(
                "'ingredient' argument must be an Ingredient in IngredientQuantity init"
            )

        if not isinstance(unit, Unit):
            raise TypeError("'unit' argument must be a Unit in IngredientQuantity init")

        if (unit == Unit.BOOL) and (quantity is not True):
            raise TypeError(
                "Error in IngredientQuantity init: if unit is BOOL, then quantity must be True"
            )

        self.ingredient = ingredient
        self.unit = unit
        self.quantity = quantity

    def __add__(self, other: "IngredientQuantity") -> "IngredientQuantity":
        if not isinstance(other, IngredientQuantity):
            raise TypeError(
                "Error in IngredientQuantity.__add__: 'other' must be of type IngredientQuantity"
            )

        if self.ingredient != other.ingredient:
            raise TypeError(
                "Error in IngredientQuantity.__add__: both operands must have the same ingredient field"
            )

        if self.unit != other.unit:
            raise TypeError(
                "Error in IngredientQuantity.__add__: both operands must have the same unit field"
            )

        if self.unit == Unit.BOOL:
            return IngredientQuantity(self.ingredient, Unit.BOOL, self.quantity or other.quantity)

        return IngredientQuantity(self.ingredient, self.unit, self.quantity + other.quantity)

    def __eq__(self, other) -> bool:
        return all(
            (
                self.ingredient == other.ingredient,
                self.unit == other.unit,
                self.quantity == other.quantity,
            )
        )

    def __repr__(self) -> str:
        return f"IngredientQuantity({self.ingredient!r}, {self.unit!r}, {self.quantity!r})"


class IngredientQuantityCollection:
    def __init__(self, ingredient_quantities: Iterable[IngredientQuantity]):
        self.ingredient_quantities = tuple(x for x in ingredient_quantities)

        for x in self.ingredient_quantities:
            if not isinstance(x, IngredientQuantity):
                raise TypeError(
                    f"{x} is not an IngredientQuantity in IngredientQuantityCollection init"
                )

    def __iter__(self):
        return BasicIterator(self.ingredient_quantities)

    def __eq__(self, other: "IngredientQuantityCollection") -> bool:
        if not isinstance(other, IngredientQuantityCollection):
            return False

        if len(self.ingredient_quantities) != len(other.ingredient_quantities):
            return False

        for x in self:
            if x not in other:
                return False

        return True
