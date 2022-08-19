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
    BOOL = auto()
    GRAM = auto()
    MILLILITRE = auto()
    NUMBER = auto()

    def __repr__(self) -> str:
        return f"Unit.{self.name}"


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
