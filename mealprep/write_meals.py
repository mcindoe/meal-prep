from mealprep.loc import ROOT_DIR
from mealprep.meal import Meals
from mealprep.recipe.writing import write_meal_as_recipe


MEAL_DIR = ROOT_DIR / "data/meals"


for meal in Meals.values():
    file_name = f"{meal.name}.yaml"
    file_path = MEAL_DIR / file_name
    write_meal_as_recipe(meal, file_path)
