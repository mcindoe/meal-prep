from enum import Enum


class RecipeError(BaseException):
    pass


class RecipeEntry(Enum):
    NAME = "Name", True, 0
    INGREDIENTS = "Ingredients", True, 1
    PROPERTIES = "Properties", True, 2
    TAGS = "Tags", False, 3

    def __init__(self, entry_name: str, required: bool, recipe_index: int):
        self.entry_name = entry_name
        self.required = required
        self.recipe_index = recipe_index
