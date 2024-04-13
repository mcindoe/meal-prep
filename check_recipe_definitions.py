"""
Check that all recipes can be loaded without error
"""

from mealprep.recipe.reading import get_project_defined_meals


if __name__ == "__main__":
    get_project_defined_meals()
