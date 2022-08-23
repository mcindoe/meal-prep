from enum import Enum, auto


class BaseEnum(Enum):
    @classmethod
    def values(cls) -> set:
        return {x.value for x in cls}

    @classmethod
    def names(cls) -> set:
        return {x.name for x in cls}


class ConfigEntries(BaseEnum):
    DATES = "dates"
    EMAIL_ADDRESSES = "email_addresses"
    RULES = "rules"

    def __repr__(self) -> str:
        return f"ConfigEntries.{self.name}"


class Unit(BaseEnum):
    BOOL = 1, "bool", "bool"
    GRAM = 2, "gram", "grams"
    MILLILITRE = 3, "ml", "mls"
    NUMBER = 4, "unit", "units"

    def __init__(self, order, singular, plural):
        self.order = order
        self.singular = singular
        self.plural = plural

    def __repr__(self) -> str:
        return f"Unit.{self.name}"


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

    def __repr__(self) -> str:
        return f"Category.{self.name}"


class MealMetadata(BaseEnum):
    pass


class MealProperty(MealMetadata):
    MEAT = auto()

    def __repr__(self) -> str:
        return f"MealProperty.{self.name}"


class MealTag(MealMetadata):
    ROAST = auto()
    PASTA = auto()
    VEGETARIAN = auto()

    def __repr__(self) -> str:
        return f"MealTag.{self.name}"


class MealMeat(BaseEnum):
    BEEF = auto()
    CHICKEN = auto()
    LAMB = auto()
    NONE = auto()
    PORK = auto()

    def __repr__(self) -> str:
        return f"MealMeat.{self.name}"
