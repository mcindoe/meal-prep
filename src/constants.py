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


class Unit(BaseEnum):
    BOOL = auto()
    GRAM = auto()
    MILLILITRES = auto()
    NUMBER = auto()


class Category(BaseEnum):
    CAN = auto()
    CARBOHYDRATE = auto()
    CONDIMENT = auto()
    DAIRY = auto()
    FRUIT = auto()
    HERB = auto()
    MEAT = auto()
    SAUCE = auto()
    SPICE = auto()
    VEGETABLE = auto()


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
