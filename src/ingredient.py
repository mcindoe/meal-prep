from typing import Any
from typing import Iterable

from mealprep.src.basic_iterator import BasicIterator
from mealprep.src.constants import BaseEnum
from mealprep.src.constants import Category
from mealprep.src.constants import Unit


class Ingredient:
    def __init__(self, name: str, category: Category):
        if not isinstance(name, str):
            raise TypeError("'name' argument must be a string in Ingredient init")
        if not isinstance(category, Category):
            raise TypeError("'category' argument must be a Category in Ingredient init")

        self.name = name
        self.category = category


class IngredientQuantity:
    def __init__(self, ingredient: Ingredient, unit: Unit, quantity: Any):
        if not isinstance(ingredient, Ingredients):
            raise TypeError(
                "'ingredient' argument must be in the Ingredients enum in IngredientQuantity init"
            )
        if not isinstance(unit, Unit):
            raise TypeError(
                "'unit' argument must be a Unit in IngredientQuantity init"
            )

        if unit is Unit.BOOL and quantity is not True:
            raise TypeError(
                "Error in IngredientQuantity init: if unit is BOOL, then quantity must be True"
            )

        self.ingredient = ingredient
        self.unit = unit
        self.quantity = quantity

    def __add__(self, other: "IngredientQuantity") -> "IngredientQuantity":
        if not isinstance(other, IngredientQuantity):
            raise TypeError("Error in IngredientQuantity.__add__: 'other' must be of type IngredientQuantity")

        if self.ingredient is not other.ingredient:
            raise TypeError("Error in IngredientQuantity.__add__: both operands must have the same ingredient field")

        if self.unit is not other.unit:
            raise TypeError("Error in IngredientQuantity.__add__: both operands must have the same unit field")

        if self.unit is Unit.BOOL:
            return IngredientQuantity(self.ingredient, Unit.BOOL, self.quantity or other.quantity)

        return IngredientQuantity(self.ingredient, self.unit, self.quantity + other.quantity)

    def __eq__(self, other) -> bool:
        return all((
            self.ingredient == other.ingredient,
            self.unit == other.unit,
            self.quantity == other.quantity
        ))

    def __repr__(self) -> str:
        return f"IngredientQuantity({self.ingredient!r}, {self.unit!r}, {self.quantity!r})"


class IngredientQuantityCollection:
    def __init__(self, ingredient_quantities: Iterable[IngredientQuantity]):
        self.ingredient_quantities = tuple(x for x in ingredient_quantities)

        for x in self.ingredient_quantities:
            if not isinstance(x, IngredientQuantity):
                raise TypeError(f"{x} is not an IngredientQuantity in IngredientQuantityCollection init")

    def __iter__(self):
        return BasicIterator(self.ingredient_quantities)


class Ingredients(BaseEnum):
    AUBERGINE = Ingredient("Aubergine", Category.VEGETABLE)
    BABY_SPINACH = Ingredient("Baby Spinach", Category.VEGETABLE)
    BABY_CORN = Ingredient("Baby Corn", Category.VEGETABLE)
    BACON = Ingredient("Bacon", Category.MEAT)
    BASIL = Ingredient("Basil", Category.HERB)
    BALSAMIC_VINEGAR = Ingredient("Balsamic Vinegar", Category.SAUCE)
    BAY_LEAVES = Ingredient("Bay Leaves", Category.HERB)
    BEEF_CHUCK_STEAK = Ingredient("Beef Chuck Steak", Category.MEAT)
    BEEF_JOINT = Ingredient("Beef Joint", Category.MEAT)
    BEEF_MINCE = Ingredient("Beef Mince", Category.MEAT)
    BEEF_STOCK = Ingredient("Beef Stock", Category.SAUCE)
    BONELESS_LEG_OF_LAMB = Ingredient("Boneless Leg of Lamb", Category.MEAT)
    BREADCRUMBS = Ingredient("Breadcrumbs", Category.CARBOHYDRATE)
    BROWN_SUGAR = Ingredient("Brown Sugar", Category.CONDIMENT)
    BURGER_BUNS = Ingredient("Burger Buns", Category.CARBOHYDRATE)
    BUTTER = Ingredient("Butter", Category.DAIRY)
    CARDAMOM = Ingredient("Cardamom", Category.SPICE)
    CARROT = Ingredient("Carrot", Category.VEGETABLE)
    CASTER_SUGAR = Ingredient("Caster Sugar", Category.CONDIMENT)
    CAYENNE_PEPPER = Ingredient("Cayenne Pepper", Category.SPICE)
    CELERY = Ingredient("Celery", Category.VEGETABLE)
    CHEDDAR_CHEESE = Ingredient("Cheddar Cheese", Category.DAIRY)
    CHERRY_TOMATOES = Ingredient("Cherry Tomatoes", Category.VEGETABLE)
    CHICKEN_BREAST = Ingredient("Chicken Breast", Category.MEAT)
    CHICKEN_STOCK = Ingredient("Chicken Stock", Category.SAUCE)
    CHICKEN_THIGH = Ingredient("Chicken Thigh", Category.MEAT)
    CHOPPED_TOMATOES = Ingredient("Chopped Tomatoes", Category.CAN)
    CINAMMON = Ingredient("Cinammon", Category.SPICE)
    CINAMMON_STICKS = Ingredient("Cinammon Sticks", Category.SPICE)
    CORIANDER = Ingredient("Coriander", Category.HERB)
    CREAM = Ingredient("Cream", Category.DAIRY)
    CUMIN = Ingredient("Cumin", Category.SPICE)
    DARK_SOY_SAUCE = Ingredient("Dark Soy Sauce", Category.SAUCE)
    DIJON_MUSTARD = Ingredient("Dijon Mustard", Category.CONDIMENT)
    DOUBLE_CREAM = Ingredient("Double Cream", Category.DAIRY)
    DRIED_MUSTARD = Ingredient("Dried Mustard", Category.CONDIMENT)
    EGGS = Ingredient("Eggs", Category.DAIRY)
    FRESH_CHILLI = Ingredient("Fresh Chilli", Category.VEGETABLE)
    FRESH_LEMON_JUICE = Ingredient("Fresh Lemon Juice", Category.CONDIMENT)
    FLOUR = Ingredient("Flour", Category.CONDIMENT)
    FULL_FAT_CREAM_CHEESE = Ingredient("Full Fat Cream Cheese", Category.DAIRY)
    GARLIC_CLOVE = Ingredient("Garlic Clove", Category.VEGETABLE)
    GINGER = Ingredient("Ginger", Category.VEGETABLE)
    GREEN_BEANS = Ingredient("Green Beans", Category.VEGETABLE)
    GREEN_PESTO = Ingredient("Green Pesto", Category.SAUCE)
    GRUYERE_CHEESE = Ingredient("Gruyere Cheese", Category.DAIRY)
    GUINNESS = Ingredient("Guinness", Category.SAUCE)
    HONEY = Ingredient("Honey", Category.CONDIMENT)
    KIDNEY_BEANS = Ingredient("Kidney Beans", Category.CAN)
    LAMB_MINCE = Ingredient("Lamb Mince", Category.MEAT)
    LAMB_STOCK = Ingredient("Lamb Stock", Category.SAUCE)
    LASAGNE_SHEETS = Ingredient("Lasagne Sheets", Category.CARBOHYDRATE)
    LEG_OF_LAMB = Ingredient("Leg of Lamb", Category.MEAT)
    LEMON = Ingredient("Lemon", Category.VEGETABLE)
    LEMONGRASS_PASTE = Ingredient("Lemongrass Paste", Category.CONDIMENT)
    LENTILS = Ingredient("Lentils", Category.CAN)
    LETTUCE = Ingredient("Lettuce", Category.VEGETABLE)
    LONG_GRAIN_RICE = Ingredient("Long-Grain Rice", Category.CARBOHYDRATE)
    MAYONNAISE = Ingredient("Mayonnaise", Category.SAUCE)
    MEDIUM_CURRY_POWDER = Ingredient("Medium Curry Powder", Category.SPICE)
    MILK = Ingredient("Milk", Category.DAIRY)
    MIXED_HERBS = Ingredient("Mixed Herbs", Category.HERB)
    MOZARELLA_CHEESE = Ingredient("Mozarella Cheese", Category.DAIRY)
    NUTMEG = Ingredient("Nutmeg", Category.SPICE)
    OLIVE_OIL = Ingredient("Olive Oil", Category.CONDIMENT)
    ONION = Ingredient("Onion", Category.VEGETABLE)
    OREGANO = Ingredient("Oregano", Category.HERB)
    PAK_CHOI = Ingredient("Pak Choi", Category.VEGETABLE)
    PAPRIKA = Ingredient("Paprika", Category.SPICE)
    PARMESAN_CHEESE = Ingredient("Parmesan Cheese", Category.DAIRY)
    PARSLEY = Ingredient("Parsley", Category.HERB)
    PEAR = Ingredient("Pear", Category.FRUIT)
    PENNE_PASTA = Ingredient("Penne Pasta", Category.CARBOHYDRATE)
    PLUM_TOMATOES = Ingredient("Plum Tomatoes", Category.VEGETABLE)
    PORK_BELLY_SLICE = Ingredient("Pork Belly Slice", Category.MEAT)
    PORK_JOINT = Ingredient("Pork Joint", Category.MEAT)
    PORK_MINCE = Ingredient("Pork Mince", Category.MEAT)
    POTATO = Ingredient("Potato", Category.VEGETABLE)
    RAW_KING_PRAWNS = Ingredient("Raw King Prawns", Category.FISH)
    RED_CHILLI = Ingredient("Red Chilli", Category.VEGETABLE)
    RED_ONION = Ingredient("Red Onion", Category.VEGETABLE)
    RED_PEPPER = Ingredient("Red Pepper", Category.VEGETABLE)
    RED_WINE = Ingredient("Red Wine", Category.CONDIMENT)
    REDCURRANT_JELLY = Ingredient("Redcurrant Jelly", Category.CONDIMENT)
    RICE = Ingredient("Rice", Category.CARBOHYDRATE)
    RICE_WINE = Ingredient("Rice Wine", Category.SAUCE)
    SALMON_FILLET = Ingredient("Salmon Fillet", Category.FISH)
    SHORTCRUST_PASTRY = Ingredient("Shortcrust Pastry", Category.CARBOHYDRATE)
    SMOKED_HADDOCK_FILLET = Ingredient("Smoked Haddock Fillet", Category.FISH)
    SOY_SAUCE = Ingredient("Soy Sauce", Category.CONDIMENT)
    SPAGHETTI = Ingredient("Spaghetti", Category.CARBOHYDRATE)
    SWEET_CHILLI_SAUCE = Ingredient("Sweet Chilli Sauce", Category.CONDIMENT)
    STEWING_BEEF = Ingredient("Stewing Beef", Category.MEAT)
    SUNDRIED_TOMATOES = Ingredient("Sundried Tomatoes", Category.CAN)
    SUNFLOWER_OIL = Ingredient("Sunflower Oil", Category.CONDIMENT)
    TALEGGIO_CHEESE = Ingredient("Taleggio Cheese", Category.DAIRY)
    THYME = Ingredient("Thyme", Category.HERB)
    TOMATO = Ingredient("Tomato", Category.VEGETABLE)
    TOMATO_PUREE = Ingredient("Tomato Puree", Category.CONDIMENT)
    TORTILLA_WRAPS = Ingredient("Tortilla Wraps", Category.CARBOHYDRATE)
    TUMERIC = Ingredient("Tumeric", Category.SPICE)
    VEGETABLE_OIL = Ingredient("Vegetable Oil", Category.CONDIMENT)
    VEGETABLE_STOCK = Ingredient("Vegetable Stock", Category.SAUCE)
    VERMICELLI_NOODLES = Ingredient("Vermicelli Noodles", Category.CARBOHYDRATE)
    VINE_CHERRY_TOMATOES = Ingredient("Vine Cherry Tomatoes", Category.VEGETABLE)
    WHOLE_CHICKEN = Ingredient("Whole Chicken", Category.MEAT)
    WORCESTERSHIRE_SAUCE = Ingredient("Worcestershire Sauce", Category.SAUCE)
    YELLOW_PEPPER = Ingredient("Yellow Pepper", Category.VEGETABLE)
