from pathlib import Path


ROOT_DIR = Path(__file__).parents[1]
DATA_DIR = ROOT_DIR / "data"
RECIPES_DIR = DATA_DIR / "recipes"
SHOPPING_LIST_DIR = DATA_DIR / "shoppingLists"

SUPPORTED_INGREDIENT_INFO_FILE_PATH = DATA_DIR / "ingredients.csv"
PROJECT_MEAL_DIARY_FILE_PATH = DATA_DIR / "meal_diary.json"

INCLUDED_RECIPES_DIR = RECIPES_DIR / "included"
EXCLUDED_RECIPES_DIR = RECIPES_DIR / "excluded"
