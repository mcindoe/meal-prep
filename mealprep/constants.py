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
    BOOL = 1, None, None, None
    BAG = 2, "bag", "bags", None
    JAR = 3, "jar", "jars", None
    GRAM = 4, "gram", "grams", "g"
    MILLILITRE = 5, "ml", "ml", "ml"
    NUMBER = 6, "unit", "units", None

    def __init__(self, order, singular, plural, abbreviation):
        self.order = order
        self.singular = singular
        self.plural = plural
        self.abbreviation = abbreviation


# Mapping from all unit descriptions back to the unit. E.g. g, gram, grams -> Unit.GRAM
UNIT_IDENTIFIERS = {}
for unit in Unit:
    for attribute_name in ("singular", "plural", "abbreviation"):
        unit_attribute_value = getattr(unit, attribute_name)
        if unit_attribute_value is not None:
            assert (unit_attribute_value not in UNIT_IDENTIFIERS) or (
                UNIT_IDENTIFIERS[unit_attribute_value] == unit
            )
            UNIT_IDENTIFIERS[unit_attribute_value] = unit


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


class MealMeat(BaseEnum):
    BEEF = "Beef"
    CHICKEN = "Chicken"
    FISH = "Fish"
    LAMB = "Lamb"
    NONE = "None"
    PORK = "Pork"
    TURKEY = "Turkey"


class MealProperty(MealMetadata):
    MEAT = "Meat", MealMeat

    def __init__(self, description: str, supported_values: BaseEnum):
        self.description = description
        self.supported_values = supported_values


class MealTag(MealMetadata):
    INDIAN = "Indian"
    ROAST = "Roast"
    PASTA = "Pasta"
    VEGETARIAN = "Vegetarian"
    WINTER = "Winter"
