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
    FRUIT = auto()
    VEGETABLE = auto()
    HERB = auto()
    CARBOHYDRATE = auto()
    DAIRY = auto()
    MEAT = auto()
    CAN = auto()
    CONDIMENT = auto()
    SAUCE = auto()
    SPICE = auto()

    def __init__(self, order):
        self.order = order

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
