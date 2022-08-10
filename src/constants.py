from enum import Enum, auto


class BaseEnum(Enum):
    @classmethod
    def values(cls) -> set:
        return {x.value for x in cls}

    @classmethod
    def names(cls) -> set:
        return {x.name for x in cls}


class ConfigEntries(BaseEnum):
    EMAIL_ADDRESSES = "email_addresses"


class Unit(BaseEnum):
    BOOL = auto()
    GRAM = auto()
    MILLILITRES = auto()


class Category(BaseEnum):
    FRUIT = auto()
    HERB = auto()
    MEAT = auto()
    VEGETABLE = auto()
