from typing import Any, Iterable

from mealprep.basic_iterator import BasicIterator
from mealprep.constants import BaseEnum, Category, Unit


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
            raise TypeError("'unit' argument must be a Unit in IngredientQuantity init")

        if unit is Unit.BOOL and quantity is not True:
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

        if self.ingredient is not other.ingredient:
            raise TypeError(
                "Error in IngredientQuantity.__add__: both operands must have the same ingredient field"
            )

        if self.unit is not other.unit:
            raise TypeError(
                "Error in IngredientQuantity.__add__: both operands must have the same unit field"
            )

        if self.unit is Unit.BOOL:
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


# TODO: Perhaps a CSV for these? Do I ever need to enumerate over these? I can just generate a runtime list
# of available options if I need to do that?
# Or, perhaps it's okay to keep this enum, but let's just be careful about how it's used
class Ingredients(BaseEnum):
    ACTIVE_DRY_YEAST = Ingredient("Active Dry Yeast", Category.CONDIMENT)
    AUBERGINE = Ingredient("Aubergine", Category.VEGETABLE)
    BABY_CORN = Ingredient("Baby Corn", Category.VEGETABLE)
    BABY_CARROT = Ingredient("Baby Carrot", Category.VEGETABLE)
    BABY_RED_POTATO = Ingredient("Baby Red Potato", Category.VEGETABLE)
    BABY_SPINACH = Ingredient("Baby Spinach", Category.VEGETABLE)
    BACON = Ingredient("Bacon", Category.MEAT)
    BALSAMIC_VINEGAR = Ingredient("Balsamic Vinegar", Category.SAUCE)
    BASIL = Ingredient("Basil", Category.HERB)
    BASMATI_RICE = Ingredient("Basmati Rice", Category.CARBOHYDRATE)
    BAY_LEAVES = Ingredient("Bay Leaves", Category.HERB)
    BEEF_BROTH = Ingredient("Beef Broth", Category.SAUCE)
    BEEF_CHUCK_STEAK = Ingredient("Beef Chuck Steak", Category.MEAT)
    BEEF_JOINT = Ingredient("Beef Joint", Category.MEAT)
    BEEF_MINCE = Ingredient("Beef Mince", Category.MEAT)
    BEEF_STOCK = Ingredient("Beef Stock", Category.SAUCE)
    BONELESS_LEG_OF_LAMB = Ingredient("Boneless Leg of Lamb", Category.MEAT)
    BONELESS_SKINLESS_CHICKEN_THIGH = Ingredient("Boneless Skinless Chicken Thigh", Category.MEAT)
    BREADCRUMBS = Ingredient("Breadcrumbs", Category.CARBOHYDRATE)
    BROWN_SUGAR = Ingredient("Brown Sugar", Category.CONDIMENT)
    BURGER_BUNS = Ingredient("Burger Buns", Category.CARBOHYDRATE)
    BUTTER = Ingredient("Butter", Category.DAIRY)
    CAPERS = Ingredient("Capers", Category.CONDIMENT)
    CAPUTO_DOUBLE_ZERO_FLOUR = Ingredient("Caputo 00 Flour", Category.CONDIMENT)
    CARDAMOM = Ingredient("Cardamom", Category.SPICE)
    CARROT = Ingredient("Carrot", Category.VEGETABLE)
    CASTER_SUGAR = Ingredient("Caster Sugar", Category.CONDIMENT)
    CAULIFLOWER_FLOURET = Ingredient("Cauliflower Flouret", Category.VEGETABLE)
    CAYENNE_PEPPER = Ingredient("Cayenne Pepper", Category.SPICE)
    CELERY = Ingredient("Celery", Category.VEGETABLE)
    CHEDDAR_CHEESE = Ingredient("Cheddar Cheese", Category.DAIRY)
    CHERRY_TOMATOES = Ingredient("Cherry Tomatoes", Category.VEGETABLE)
    CHICKEN_BREAST = Ingredient("Chicken Breast", Category.MEAT)
    CHICKEN_BROTH = Ingredient("Chicken Broth", Category.SAUCE)
    CHICKEN_STOCK = Ingredient("Chicken Stock", Category.SAUCE)
    CHICKEN_THIGH = Ingredient("Chicken Thigh", Category.MEAT)
    CHIVES = Ingredient("Chives", Category.HERB)
    CHOPPED_TOMATOES = Ingredient("Chopped Tomatoes", Category.CAN)
    CINAMMON = Ingredient("Cinammon", Category.SPICE)
    CINAMMON_STICK = Ingredient("Cinammon Stick", Category.SPICE)
    CIPOLLINI_ONION = Ingredient("Cipollini Onion", Category.VEGETABLE)
    COCONUT_MILK = Ingredient("Coconut Milk", Category.CONDIMENT)
    COCONUT_OIL = Ingredient("Coconut Oil", Category.CONDIMENT)
    COMPRESSED_YEAST = Ingredient("Compressed Yeast", Category.CONDIMENT)
    CORIANDER = Ingredient("Coriander", Category.HERB)
    CREAM = Ingredient("Cream", Category.DAIRY)
    CUMIN = Ingredient("Cumin", Category.SPICE)
    DARK_SOY_SAUCE = Ingredient("Dark Soy Sauce", Category.SAUCE)
    DIJON_MUSTARD = Ingredient("Dijon Mustard", Category.CONDIMENT)
    DOUBLE_CREAM = Ingredient("Double Cream", Category.DAIRY)
    DRIED_BASIL = Ingredient("Dried Basil", Category.HERB)
    DRIED_FENUGREEK = Ingredient("Dried Fenugreek", Category.CONDIMENT)
    DRIED_MUSTARD = Ingredient("Dried Mustard", Category.CONDIMENT)
    DRIED_THYME = Ingredient("Dried Thyme", Category.HERB)
    DRIED_OREGANO = Ingredient("Dried Oregano", Category.HERB)
    DRY_RED_WINE = Ingredient("Dry Red Wine", Category.CONDIMENT)
    EGGS = Ingredient("Eggs", Category.DAIRY)
    FLOUR = Ingredient("Flour", Category.CONDIMENT)
    FRESH_CHILLI = Ingredient("Fresh Chilli", Category.VEGETABLE)
    FRESH_LEMON_JUICE = Ingredient("Fresh Lemon Juice", Category.CONDIMENT)
    FRESH_TARRAGON = Ingredient("Fresh Tarragon", Category.HERB)
    FROZEN_PEAS = Ingredient("Frozen Peas", Category.VEGETABLE)
    FULL_FAT_CREAM_CHEESE = Ingredient("Full Fat Cream Cheese", Category.DAIRY)
    GARAM_MASALA = Ingredient("Garam Masala", Category.SPICE)
    GARLIC_CLOVE = Ingredient("Garlic Clove", Category.VEGETABLE)
    GARLIC_POWDER = Ingredient("Garlic Powder", Category.VEGETABLE)
    GHEE = Ingredient("Ghee", Category.CONDIMENT)
    GINGER = Ingredient("Ginger", Category.VEGETABLE)
    GREEN_BEANS = Ingredient("Green Beans", Category.VEGETABLE)
    GREEN_PEPPER = Ingredient("Green Pepper", Category.VEGETABLE)
    GREEN_PESTO = Ingredient("Green Pesto", Category.SAUCE)
    GRUYERE_CHEESE = Ingredient("Gruyere Cheese", Category.DAIRY)
    GUINNESS = Ingredient("Guinness", Category.SAUCE)
    HAM = Ingredient("Ham", Category.MEAT)
    HONEY = Ingredient("Honey", Category.CONDIMENT)
    ITALIAN_HERBS = Ingredient("Italian Herbs", Category.HERB)
    JALAPENO = Ingredient("Jalapeno", Category.VEGETABLE)
    KETCHUP = Ingredient("Ketchup", Category.CONDIMENT)
    KIDNEY_BEANS = Ingredient("Kidney Beans", Category.CAN)
    KOSHER_SALT = Ingredient("Kosher Salt", Category.CONDIMENT)
    LAMB_MINCE = Ingredient("Lamb Mince", Category.MEAT)
    LAMB_STOCK = Ingredient("Lamb Stock", Category.SAUCE)
    LASAGNE_SHEETS = Ingredient("Lasagne Sheets", Category.CARBOHYDRATE)
    LEEK = Ingredient("Leek", Category.VEGETABLE)
    LEG_OF_LAMB = Ingredient("Leg of Lamb", Category.MEAT)
    LEMON = Ingredient("Lemon", Category.VEGETABLE)
    LEMONGRASS_PASTE = Ingredient("Lemongrass Paste", Category.CONDIMENT)
    LEMON_JUICE = Ingredient("Lemon Juice", Category.CONDIMENT)
    LENTILS = Ingredient("Lentils", Category.CAN)
    LETTUCE = Ingredient("Lettuce", Category.VEGETABLE)
    LIGHT_COCONUT_MILK = Ingredient("Light Coconut Milk", Category.CONDIMENT)
    LIME = Ingredient("Lime", Category.VEGETABLE)
    LINGUINE = Ingredient("Linguine", Category.CARBOHYDRATE)
    LONG_GRAIN_RICE = Ingredient("Long-Grain Rice", Category.CARBOHYDRATE)
    MATURE_CHEDDAR_CHEESE = Ingredient("Mature Cheddar Cheese", Category.DAIRY)
    MAYONNAISE = Ingredient("Mayonnaise", Category.SAUCE)
    MEDIUM_CURRY_POWDER = Ingredient("Medium Curry Powder", Category.SPICE)
    MILK = Ingredient("Milk", Category.DAIRY)
    MINI_CARROTS = Ingredient("Mini Carrots", Category.VEGETABLE)
    MIXED_HERBS = Ingredient("Mixed Herbs", Category.HERB)
    MOZARELLA_CHEESE = Ingredient("Mozarella Cheese", Category.DAIRY)
    MRS_JAMISONS_ORGANIC_CHICKEN_BASE = Ingredient(
        "Mrs Jamison's Organic Chicken Base", Category.CONDIMENT
    )
    NUTMEG = Ingredient("Nutmeg", Category.SPICE)
    OLIVE_OIL = Ingredient("Olive Oil", Category.CONDIMENT)
    ONION = Ingredient("Onion", Category.VEGETABLE)
    OREGANO = Ingredient("Oregano", Category.HERB)
    PAK_CHOI = Ingredient("Pak Choi", Category.VEGETABLE)
    PANEER_CHEESE = Ingredient("Paneer Cheese", Category.DAIRY)
    PAPRIKA = Ingredient("Paprika", Category.SPICE)
    PARMESAN_CHEESE = Ingredient("Parmesan Cheese", Category.DAIRY)
    PARSLEY = Ingredient("Parsley", Category.HERB)
    PASSATA = Ingredient("Passata", Category.VEGETABLE)
    PEAR = Ingredient("Pear", Category.FRUIT)
    PENNE_PASTA = Ingredient("Penne Pasta", Category.CARBOHYDRATE)
    PEPPERONI = Ingredient("Pepperoni", Category.MEAT)
    PLUM_TOMATOES = Ingredient("Plum Tomatoes", Category.VEGETABLE)
    PORK_BELLY_SLICE = Ingredient("Pork Belly Slice", Category.MEAT)
    PORK_JOINT = Ingredient("Pork Joint", Category.MEAT)
    PORK_MINCE = Ingredient("Pork Mince", Category.MEAT)
    POTATO = Ingredient("Potato", Category.VEGETABLE)
    PROSCIUTTO = Ingredient("Prosciutto", Category.MEAT)
    RAW_KING_PRAWNS = Ingredient("Raw King Prawns", Category.FISH)
    READY_ROLLED_PUFF_PASTRY = Ingredient("Ready Rolled Puff Pastry", Category.CARBOHYDRATE)
    REDCURRANT_JELLY = Ingredient("Redcurrant Jelly", Category.CONDIMENT)
    RED_CHILLI = Ingredient("Red Chilli", Category.VEGETABLE)
    RED_ONION = Ingredient("Red Onion", Category.VEGETABLE)
    RED_PEPPER = Ingredient("Red Pepper", Category.VEGETABLE)
    RED_PEPPER_FLAKES = Ingredient("Red Pepper Flakes", Category.CONDIMENT)
    RED_WINE = Ingredient("Red Wine", Category.CONDIMENT)
    RICE = Ingredient("Rice", Category.CARBOHYDRATE)
    RICE_WINE = Ingredient("Rice Wine", Category.SAUCE)
    SALMON_FILLET = Ingredient("Salmon Fillet", Category.FISH)
    SHALLOT = Ingredient("Shallot", Category.VEGETABLE)
    SHELLED_PISTACHIOS = Ingredient("Shelled Pistachios", Category.CONDIMENT)
    SHORTCRUST_PASTRY = Ingredient("Shortcrust Pastry", Category.CARBOHYDRATE)
    SMOKED_HADDOCK_FILLET = Ingredient("Smoked Haddock Fillet", Category.FISH)
    SOY_SAUCE = Ingredient("Soy Sauce", Category.CONDIMENT)
    SPAGHETTI = Ingredient("Spaghetti", Category.CARBOHYDRATE)
    SPINACH = Ingredient("Spinach", Category.VEGETABLE)
    STEWING_BEEF = Ingredient("Stewing Beef", Category.MEAT)
    SUNDRIED_TOMATOES = Ingredient("Sundried Tomatoes", Category.CAN)
    SUNFLOWER_OIL = Ingredient("Sunflower Oil", Category.CONDIMENT)
    SWEET_CHILLI_SAUCE = Ingredient("Sweet Chilli Sauce", Category.CONDIMENT)
    SWEET_POTATO = Ingredient("Sweet Potato", Category.VEGETABLE)
    TALEGGIO_CHEESE = Ingredient("Taleggio Cheese", Category.DAIRY)
    THICK_CUT_BACON = Ingredient("Thick Cut Bacon", Category.MEAT)
    THYME = Ingredient("Thyme", Category.HERB)
    TOMATO = Ingredient("Tomato", Category.VEGETABLE)
    TOMATO_PASTE = Ingredient("Tomato Paste", Category.CONDIMENT)
    TOMATO_PUREE = Ingredient("Tomato Puree", Category.CONDIMENT)
    TOMATO_SOUP = Ingredient("Tomato Soup", Category.CAN)
    TORTILLA_WRAPS = Ingredient("Tortilla Wraps", Category.CARBOHYDRATE)
    TUMERIC = Ingredient("Tumeric", Category.SPICE)
    TURKEY_MINCE = Ingredient("Turkey Mince", Category.MEAT)
    VEGETABLE_BROTH = Ingredient("Vegetable Broth", Category.SAUCE)
    VEGETABLE_OIL = Ingredient("Vegetable Oil", Category.CONDIMENT)
    VEGETABLE_STOCK = Ingredient("Vegetable Stock", Category.SAUCE)
    VERMICELLI_NOODLES = Ingredient("Vermicelli Noodles", Category.CARBOHYDRATE)
    VINE_CHERRY_TOMATOES = Ingredient("Vine Cherry Tomatoes", Category.VEGETABLE)
    WHITE_WINE = Ingredient("White Wine", Category.CONDIMENT)
    WHOLE_CHICKEN = Ingredient("Whole Chicken", Category.MEAT)
    WORCESTERSHIRE_SAUCE = Ingredient("Worcestershire Sauce", Category.SAUCE)
    YELLOW_PEPPER = Ingredient("Yellow Pepper", Category.VEGETABLE)
    YOGURT = Ingredient("Yogurt", Category.DAIRY)


UPPER_INGREDIENT_NAME_TO_INGREDIENT_MAP = {
    ingredient.value.name.upper(): ingredient for ingredient in Ingredients
}


def get_ingredient_from_name(ingredient_name: str) -> Ingredient:
    try:
        return UPPER_INGREDIENT_NAME_TO_INGREDIENT_MAP[ingredient_name.upper()]
    except KeyError as exc:
        raise ValueError(f"Unable to find an Ingredient with name {ingredient_name}") from exc
