import datetime as dt

import pytest

from mealprep.meal import Meal, MealCollection, MealDiary
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


class TestRule:
    @pytest.fixture()
    def meal_collection(self):
        yield MealCollection(
            (
                Meal.from_name("Spaghetti Bolognese"),
                Meal.from_name("Sticky Chinese Pork Belly"),
                Meal.from_name("Chicken Fajitas"),
                Meal.from_name("Fish Pie"),
                Meal.from_name("Indian Lamb with Spiced Lentils"),
                Meal.from_name("Roast Beef"),
            )
        )

    @pytest.fixture()
    def meal_diary(self):
        yield MealDiary(
            {
                dt.date(2022, 1, 1): Meal.from_name("Fish Pie"),
                dt.date(2022, 1, 2): Meal.from_name("Sticky Chinese Pork Belly"),
                dt.date(2022, 1, 3): Meal.from_name("Spaghetti Bolognese"),
                dt.date(2022, 2, 1): Meal.from_name("Indian Lamb with Spiced Lentils"),
            }
        )

    @pytest.fixture()
    def date(self):
        """
        Yield a date which is not specified in the meal_diary fixture
        """

        yield dt.date(2022, 3, 1)

    @pytest.fixture()
    def sunday_date(self):
        """
        Yield a date which was a Sunday
        """

        yield dt.date(2022, 3, 6)

    def test_exceptions(self, meal_collection, date, meal_diary):
        example_rule = Rules.FORCE_ROAST_ON_SUNDAY.value

        # meal_collection argument is not a MealCollection
        with pytest.raises(TypeError):
            example_rule(
                (
                    Meal.from_name("Spaghetti Bolognese"),
                    Meal.from_name("Sticky Chinese Pork Belly"),
                ),
                date,
                meal_diary,
            )

        # meal_diary argument is not a MealDiary
        with pytest.raises(TypeError):
            example_rule(
                meal_collection,
                date,
                {
                    dt.date(2022, 1, 1): Meal.from_name("Fish Pie"),
                    dt.date(2022, 1, 2): Meal.from_name("Sticky Chinese Pork Belly"),
                    dt.date(2022, 2, 1): Meal.from_name("Indian Lamb with Spiced Lentils"),
                },
            )

        # date specified is already in the meal_diary
        with pytest.raises(ValueError):
            example_rule(meal_collection, meal_diary.dates[0], meal_diary)

        badly_specified_rule = BadlySpecifiedRule()
        with pytest.raises(TypeError):
            badly_specified_rule(meal_collection, date, meal_diary)

    def test_abstract_rule(self, meal_collection, date, sunday_date, meal_diary):
        """
        Test general properties which apply to all rules
        """

        trivial_rule = TrivialRule()
        returned_meal_collection = trivial_rule(meal_collection, date, meal_diary)

        # Returned rule collection should be a copy, not the same instance
        assert returned_meal_collection is not meal_collection

        force_roast_on_sunday_rule = Rules.FORCE_ROAST_ON_SUNDAY.value
        returned_meal_collection = force_roast_on_sunday_rule(
            meal_collection, sunday_date, meal_diary
        )

        assert returned_meal_collection == MealCollection((Meal.from_name("Roast Beef"),))
        assert returned_meal_collection != meal_collection

    def test_force_roast_on_sunday(self, meal_collection, date, sunday_date, meal_diary):
        force_roast_on_sunday_rule = Rules.FORCE_ROAST_ON_SUNDAY.value

        sunday_collection = force_roast_on_sunday_rule(meal_collection, sunday_date, meal_diary)
        monday_collection = force_roast_on_sunday_rule(meal_collection, date, meal_diary)

        assert sunday_collection == MealCollection((Meal.from_name("Roast Beef"),))
        assert monday_collection == meal_collection

    def test_not_pasta_twice_within_five_days_rule(self, meal_collection, meal_diary):
        not_pasta_twice_within_five_days_rule = Rules.NOT_PASTA_TWICE_WITHIN_FIVE_DAYS.value

        filtered_collection = not_pasta_twice_within_five_days_rule(
            meal_collection, dt.date(2022, 1, 8), meal_diary
        )
        unfiltered_collection = not_pasta_twice_within_five_days_rule(
            meal_collection, dt.date(2022, 1, 9), meal_diary
        )

        pasta_meal = Meal.from_name("Spaghetti Bolognese")

        assert pasta_meal not in filtered_collection
        assert pasta_meal in unfiltered_collection

    def test_not_roast_on_non_sunday(self, meal_collection, date, sunday_date, meal_diary):
        not_roast_on_non_sunday_rule = Rules.NOT_ROAST_ON_NON_SUNDAY.value

        filtered_collection = not_roast_on_non_sunday_rule(meal_collection, date, meal_diary)
        unfiltered_collection = not_roast_on_non_sunday_rule(
            meal_collection, sunday_date, meal_diary
        )

        roast_meal = Meal.from_name("Roast Beef")

        assert roast_meal not in filtered_collection
        assert unfiltered_collection == meal_collection

    def test_not_same_meal_with_seven_days_rule(self, meal_collection, date, meal_diary):
        not_same_meal_within_seven_days_rule = Rules.NOT_SAME_MEAL_WITHIN_SEVEN_DAYS.value

        filtered_collection = not_same_meal_within_seven_days_rule(
            meal_collection, dt.date(2022, 1, 4), meal_diary
        )
        unfiltered_collection = not_same_meal_within_seven_days_rule(
            meal_collection, date, meal_diary
        )

        expected_missing_meals = (
            Meal.from_name("Fish Pie"),
            Meal.from_name("Sticky Chinese Pork Belly"),
            Meal.from_name("Spaghetti Bolognese"),
        )
        assert not any(x in filtered_collection for x in expected_missing_meals)
        assert unfiltered_collection == meal_collection

    def test_not_specified_meal_on_specified_date(self, meal_collection, date, meal_diary):
        chicken_fajitas_meal = Meal.from_name("Chicken Fajitas")

        not_specified_meal_on_specified_date_rule = NotSpecifiedMealOnSpecifiedDate(
            date, chicken_fajitas_meal
        )

        filtered_collection = not_specified_meal_on_specified_date_rule(
            meal_collection, date, meal_diary
        )
        unfiltered_collection = not_specified_meal_on_specified_date_rule(
            meal_collection, date + dt.timedelta(days=1), meal_diary
        )

        assert chicken_fajitas_meal not in filtered_collection
        assert unfiltered_collection == meal_collection
