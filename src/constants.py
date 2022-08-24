from enum import auto
from enum import Enum


class BaseEnum(Enum):
    @classmethod
    def values(cls) -> set:
        return {x.value for x in cls}

    @classmethod
    def names(cls) -> set:
        return {x.name for x in cls}

    def __repr__(self) -> str:
        return f"{type(self).__name__}.{self.name}"


class ConfigEntries(BaseEnum):
    DATES = "dates"
    EMAIL_ADDRESSES = "email_addresses"
    RULES = "rules"


class Unit(BaseEnum):
    BOOL = 1, "bool", "bool"
    GRAM = 2, "gram", "grams"
    MILLILITRE = 3, "ml", "mls"
    NUMBER = 4, "unit", "units"

    def __init__(self, order, singular, plural):
        self.order = order
        self.singular = singular
        self.plural = plural


# Ordering is the list to appear in shopping lists
class Category(BaseEnum):
    FRUIT = 1, "Fruit"
    VEGETABLE = 2, "Vegetables"
    HERB = 3, "Herbs"
    CARBOHYDRATE = 4, "Carbohydrates"
    DAIRY = 5, "Dairy"
    MEAT = 6, "Meat"
    CAN = 7, "Cans"
    CONDIMENT = 8, "Condiments"
    SAUCE = 9, "Sauces"
    SPICE = 10, "Spices"

    def __init__(self, order, list_header):
        self.order = order
        self.list_header = list_header


class MealMetadata(BaseEnum):
    pass


class MealProperty(MealMetadata):
    MEAT = auto()


class MealTag(MealMetadata):
    ROAST = auto()
    PASTA = auto()
    VEGETARIAN = auto()


class MealMeat(BaseEnum):
    BEEF = auto()
    CHICKEN = auto()
    LAMB = auto()
    NONE = auto()
    PORK = auto()
