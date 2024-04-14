"""
Check that all provided ingredient information can be parsed as Ingredient
instances, and that the CSV file is sorted alphabetically
"""

from mealprep.ingredient import get_supported_ingredient_info, Ingredient


if __name__ == "__main__":
    supported_ingredient_info = get_supported_ingredient_info()
    ingredient_names = list(supported_ingredient_info.keys())
    if ingredient_names != sorted(ingredient_names):
        raise RuntimeError("Provided ingredient definitions are not sorted alphabetically")

    for name in ingredient_names:
        try:
            Ingredient.from_name(name)
        except KeyError:
            raise RuntimeError(f'Unable to parse the ingredient "{name}" as an Ingredient instance')
