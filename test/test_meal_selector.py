import datetime as dt
import pytest

from mealprep.src.exceptions import OutOfMealsError
from mealprep.src.meal import Meal
from mealprep.src.meal import MealCollection
from mealprep.src.meal import MealDiary
from mealprep.src.meal_selector import MealSelector
from mealprep.src.rule import Rules
from mealprep.src.rule import RuleCollection


class TestMealSelector:
    @pytest.fixture()
    def meal_collection(self):
        yield MealCollection((
            Meal.from_name("Spaghetti Bolognese"),
            Meal.from_name("Sticky Chinese Pork Belly"),
            Meal.from_name("Chicken Fajitas"),
            Meal.from_name("Fish Pie"),
            Meal.from_name("Indian Lamb with Spiced Lentils"),
            Meal.from_name("Roast Beef"),
        ))

    @pytest.fixture()
    def rule_collection(self):
        yield RuleCollection((
            Rules.NOT_ROAST_ON_NON_SUNDAY.value,
            Rules.FORCE_ROAST_ON_SUNDAY.value,
            Rules.NOT_SAME_MEAL_WITHIN_SEVEN_DAYS.value,
        ))

    @pytest.fixture()
    def meal_diary(self):
        yield MealDiary({
            dt.date(2022, 1, 1): Meal.from_name("Fish Pie"),
            dt.date(2022, 2, 1): Meal.from_name("Indian Lamb with Spiced Lentils"),
        })

    @pytest.fixture()
    def meal_selector(self, meal_collection, rule_collection, meal_diary):
        yield MealSelector(meal_collection, rule_collection, meal_diary)

    def test_recommend(self, meal_selector, rule_collection, meal_diary):
        # Duplicate dates passed
        with pytest.raises(ValueError):
            duplicate_dates = (dt.date(2020, 1, 1),) * 2
            meal_selector.recommend(duplicate_dates, rule_collection)

        # Date already present in the passed diary
        with pytest.raises(ValueError):
            existing_dates = meal_diary.dates
            meal_selector.recommend(
                (existing_dates[0],),
                rule_collection,
                meal_diary
            )

        recommended_diary = meal_selector.recommend(
            (dt.date(2020, 1, 1), dt.date(2020, 1, 2), dt.date(2020, 2, 1)),
            rule_collection
        )
        assert isinstance(recommended_diary, MealDiary)
