from enum import Enum


class RecipeError(BaseException):
    pass


class RecipeEntry(Enum):
    INGREDIENTS = "Ingredients", True, 0
    PROPERTIES = "Properties", True, 1
    TAGS = "Tags", False, 2

    def __init__(self, entry_name: str, required: bool, recipe_index: int):
        self.entry_name = entry_name
        self.required = required
        self.recipe_index = recipe_index
