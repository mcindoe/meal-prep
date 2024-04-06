from pathlib import Path


ROOT_DIR = Path(__file__).parents[1]
DATA_DIR = ROOT_DIR / "data"
MEALS_DIR = DATA_DIR / "meals"
SHOPPING_LIST_DIR = DATA_DIR / "shoppingLists"

SUPPORTED_INGREDIENT_INFO_FILE = DATA_DIR / "ingredients.csv"
