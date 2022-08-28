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


class Category(BaseEnum):
    """
    order - order of appearance in shopping lists
    list_header - title of the category section in shopping lists
    """

    FRUIT = 1, "Fruit"
    VEGETABLE = 2, "Vegetables"
    HERB = 3, "Herbs"
    CARBOHYDRATE = 4, "Carbohydrates"
    DAIRY = 5, "Dairy"
    MEAT = 6, "Meat"
    FISH = 7, "Fish"
    CAN = 8, "Cans"
    CONDIMENT = 9, "Condiments"
    SAUCE = 10, "Sauces"
    SPICE = 11, "Spices"

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
    FISH = auto()
    LAMB = auto()
    NONE = auto()
    PORK = auto()
