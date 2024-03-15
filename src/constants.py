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
    MEALS = "meals"
    RULES = "rules"


class Unit(BaseEnum):
    BOOL = 1, "bool", "bool", None
    BAG = 2, "bag", "bags", "bags"
    JAR = 3, "jar", "jars", "jars"
    GRAM = 4, "gram", "grams", "g"
    MILLILITRE = 5, "ml", "mls", "ml"
    NUMBER = 6, "unit", "units", None

    # TODO: I think I need to separate the concept of singular and plural abbreviation
    # Otherwise what do we do about "1 jars" in the recipe :-(
    def __init__(self, order, singular, plural, abbreviation):
        self.order = order
        self.singular = singular
        self.plural = plural
        self.abbreviation = abbreviation


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
