from mealprep.loc import MEALS_DIR
from mealprep.meal import Meals
from mealprep.recipe.writing import write_meal_as_recipe


for meal in Meals.values():
    file_name = f"{meal.name}.yaml"
    file_path = MEALS_DIR / file_name
    write_meal_as_recipe(meal, file_path)
