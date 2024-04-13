import datetime as dt
import unittest

from mealprep.meal import Meal
from mealprep.meal_collection import MealCollection
from mealprep.meal_diary import MealDiary
from mealprep.recipe.reading import get_meal_from_name
from mealprep.rule import NotSpecifiedMealOnSpecifiedDate, Rule, Rules


class TrivialRule(Rule):
    @staticmethod
    def filter(
        meal_collection: MealCollection, date: dt.date, meal_diary: MealDiary
    ) -> MealCollection:
        return meal_collection


# Example of a rule which should throw an exception: returns a Meal instead of a MealCollection
class BadlySpecifiedRule(Rule):
    @staticmethod
    def filter(meal_collection: MealCollection, date: dt.date, meal_diary: MealDiary) -> Meal:
        return meal_collection.meals[0]


class TestRule(unittest.TestCase):
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

    meal_diary = MealDiary(
        {
            dt.date(2022, 1, 1): get_meal_from_name("Fish Pie"),
            dt.date(2022, 1, 2): get_meal_from_name("Sticky Chinese Pork Belly"),
            dt.date(2022, 1, 3): get_meal_from_name("Spaghetti Bolognese"),
            dt.date(2022, 2, 1): get_meal_from_name("Indian Lamb with Spiced Lentils"),
        }
    )

    # Date is not specified in the meal_diary fixture
    date = dt.date(2022, 3, 1)

    sunday_date = dt.date(2022, 3, 6)

    def test_exceptions(self):
        example_rule = Rules.FORCE_ROAST_ON_SUNDAY.value

        # meal_collection argument is not a MealCollection
        with self.assertRaises(TypeError):
            example_rule(
                (
                    get_meal_from_name("Spaghetti Bolognese"),
                    get_meal_from_name("Sticky Chinese Pork Belly"),
                ),
                self.date,
                self.meal_diary,
            )

        # meal_diary argument is not a MealDiary
        with self.assertRaises(TypeError):
            example_rule(
                self.meal_collection,
                self.date,
                {
                    dt.date(2022, 1, 1): get_meal_from_name("Fish Pie"),
                    dt.date(2022, 1, 2): get_meal_from_name("Sticky Chinese Pork Belly"),
                    dt.date(2022, 2, 1): get_meal_from_name("Indian Lamb with Spiced Lentils"),
                },
            )

        # date specified is already in the meal_diary
        with self.assertRaises(ValueError):
            example_rule(self.meal_collection, self.meal_diary.dates[0], self.meal_diary)

        badly_specified_rule = BadlySpecifiedRule()
        with self.assertRaises(TypeError):
            badly_specified_rule(self.meal_collection, self.date, self.meal_diary)

    def test_abstract_rule(self):
        """
        Test general properties which apply to all rules
        """

        trivial_rule = TrivialRule()
        returned_meal_collection = trivial_rule(self.meal_collection, self.date, self.meal_diary)

        # Returned rule collection should be a copy, not the same instance
        self.assertIsNot(returned_meal_collection, self.meal_collection)

        force_roast_on_sunday_rule = Rules.FORCE_ROAST_ON_SUNDAY.value
        returned_meal_collection = force_roast_on_sunday_rule(
            self.meal_collection, self.sunday_date, self.meal_diary
        )

        self.assertEqual(
            returned_meal_collection, MealCollection((get_meal_from_name("Roast Beef"),))
        )
        self.assertNotEqual(returned_meal_collection, self.meal_collection)

    def test_force_roast_on_sunday(self):
        force_roast_on_sunday_rule = Rules.FORCE_ROAST_ON_SUNDAY.value

        sunday_collection = force_roast_on_sunday_rule(
            self.meal_collection, self.sunday_date, self.meal_diary
        )
        monday_collection = force_roast_on_sunday_rule(
            self.meal_collection, self.date, self.meal_diary
        )

        self.assertEqual(sunday_collection, MealCollection((get_meal_from_name("Roast Beef"),)))
        self.assertEqual(monday_collection, self.meal_collection)

    def test_not_pasta_twice_within_five_days_rule(self):
        not_pasta_twice_within_five_days_rule = Rules.NOT_PASTA_TWICE_WITHIN_FIVE_DAYS.value

        filtered_collection = not_pasta_twice_within_five_days_rule(
            self.meal_collection, dt.date(2022, 1, 8), self.meal_diary
        )
        unfiltered_collection = not_pasta_twice_within_five_days_rule(
            self.meal_collection, dt.date(2022, 1, 9), self.meal_diary
        )

        pasta_meal = get_meal_from_name("Spaghetti Bolognese")

        self.assertNotIn(pasta_meal, filtered_collection)
        self.assertIn(pasta_meal, unfiltered_collection)

    def test_not_roast_on_non_sunday(self):
        not_roast_on_non_sunday_rule = Rules.NOT_ROAST_ON_NON_SUNDAY.value

        filtered_collection = not_roast_on_non_sunday_rule(
            self.meal_collection, self.date, self.meal_diary
        )
        unfiltered_collection = not_roast_on_non_sunday_rule(
            self.meal_collection, self.sunday_date, self.meal_diary
        )

        roast_meal = get_meal_from_name("Roast Beef")

        self.assertNotIn(roast_meal, filtered_collection)
        self.assertEqual(unfiltered_collection, self.meal_collection)

    def test_not_same_meal_with_seven_days_rule(self):
        not_same_meal_within_seven_days_rule = Rules.NOT_SAME_MEAL_WITHIN_SEVEN_DAYS.value

        filtered_collection = not_same_meal_within_seven_days_rule(
            self.meal_collection, dt.date(2022, 1, 4), self.meal_diary
        )
        unfiltered_collection = not_same_meal_within_seven_days_rule(
            self.meal_collection, self.date, self.meal_diary
        )

        expected_missing_meals = (
            get_meal_from_name("Fish Pie"),
            get_meal_from_name("Sticky Chinese Pork Belly"),
            get_meal_from_name("Spaghetti Bolognese"),
        )

        self.assertFalse(any(x in filtered_collection for x in expected_missing_meals))
        self.assertEqual(unfiltered_collection, self.meal_collection)

    def test_not_specified_meal_on_specified_date(self):
        chicken_fajitas_meal = get_meal_from_name("Chicken Fajitas")

        not_specified_meal_on_specified_date_rule = NotSpecifiedMealOnSpecifiedDate(
            self.date, chicken_fajitas_meal
        )

        filtered_collection = not_specified_meal_on_specified_date_rule(
            self.meal_collection, self.date, self.meal_diary
        )
        unfiltered_collection = not_specified_meal_on_specified_date_rule(
            self.meal_collection, self.date + dt.timedelta(days=1), self.meal_diary
        )

        self.assertNotIn(chicken_fajitas_meal, filtered_collection)
        self.assertEqual(unfiltered_collection, self.meal_collection)
