import datetime as dt

from mealprep.src.meal import *
from mealprep.src.rule import *

m = Meal.from_name("Example")
date = dt.date(2022, 1, 1)

md = MealDiary({
    date: m
})
print(m)
print(md)

md.to_file("data/meal_history.json")
