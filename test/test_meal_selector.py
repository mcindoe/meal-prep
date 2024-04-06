import datetime as dt
import unittest

from mealprep.meal_collection import MealCollection
from mealprep.meal_diary import MealDiary
from mealprep.meal_selector import MealSelector
from mealprep.recipe.reading import get_meal_from_name
from mealprep.rule import RuleCollection, Rules


class TestMealSelector(unittest.TestCase):
    meal_collection = MealCollection(
        (
            get_meal_from_name("Spaghetti Bolognese"),
            get_meal_from_name("Sticky Chinese Pork Belly"),
            get_meal_from_name("Chicken Fajitas"),
            get_meal_from_name("Fish Pie"),
            get_meal_from_name("Indian Lamb with Spiced Lentils"),
            get_meal_from_name("Roast Beef"),
        )
    )

    rule_collection = RuleCollection(
        (
            Rules.NOT_ROAST_ON_NON_SUNDAY.value,
            Rules.FORCE_ROAST_ON_SUNDAY.value,
            Rules.NOT_SAME_MEAL_WITHIN_SEVEN_DAYS.value,
        )
    )

    meal_diary = MealDiary(
        {
            dt.date(2022, 1, 1): get_meal_from_name("Fish Pie"),
            dt.date(2022, 2, 1): get_meal_from_name("Indian Lamb with Spiced Lentils"),
        }
    )

    meal_selector = MealSelector(meal_collection, rule_collection, meal_diary)

    def test_recommend(self):
        # Duplicate dates passed
        with self.assertRaises(ValueError):
            duplicate_dates = (dt.date(2020, 1, 1),) * 2
            self.meal_selector.recommend(duplicate_dates, self.rule_collection)

        # Date already present in the passed diary
        with self.assertRaises(ValueError):
            existing_dates = self.meal_diary.dates
            self.meal_selector.recommend(
                (existing_dates[0],), self.rule_collection, self.meal_diary
            )

        recommended_diary = self.meal_selector.recommend(
            (dt.date(2020, 1, 1), dt.date(2020, 1, 2), dt.date(2020, 2, 1)), self.rule_collection
        )
        self.assertIsInstance(recommended_diary, MealDiary)
