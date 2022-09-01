import datetime as dt
import pytest

from mealprep.src.meal import Meal
from mealprep.src.meal import MealCollection
from mealprep.src.meal import MealDiary
from mealprep.src.rule import Rule
from mealprep.src.rule import Rules

class TrivialRule(Rule):
    @staticmethod
    def filter(meal_collection: MealCollection, date: dt.date, meal_diary: MealDiary) -> MealCollection:
        return meal_collection


# Example of a rule which should throw an exception: returns a Meal
# instead of a MealCollection
class BadlySpecifiedRule(Rule):
	@staticmethod
	def filter(meal_collection: MealCollection, date: dt.date, meal_diary: MealDiary) -> Meal:
		return meal_collection.meals[0]


class TestRule:
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
	def meal_diary(self):
		yield MealDiary({
			dt.date(2022, 1, 1): Meal.from_name("Fish Pie"),
			dt.date(2022, 1, 2): Meal.from_name("Sticky Chinese Pork Belly"),
			dt.date(2022, 2, 1): Meal.from_name("Indian Lamb with Spiced Lentils")
		})

	@pytest.fixture()
	def date(self):
		"""
		Yield a date which is not specified in the meal_diary fixture
		"""

		yield dt.date(2022, 3, 1)

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
				meal_diary
			)

		# meal_diary argument is not a MealDiary
		with pytest.raises(TypeError):
			example_rule(
				meal_collection,
				date,
				{
					dt.date(2022, 1, 1): Meal.from_name("Fish Pie"),
					dt.date(2022, 1, 2): Meal.from_name("Sticky Chinese Pork Belly"),
					dt.date(2022, 2, 1): Meal.from_name("Indian Lamb with Spiced Lentils")
				}
			)

		# date specified is already in the meal_diary
		with pytest.raises(ValueError):
			example_rule(
				meal_collection,
				meal_diary.dates[0],
				meal_diary
			)

		badly_specified_rule = BadlySpecifiedRule()
		with pytest.raises(TypeError):
			badly_specified_rule(
				meal_collection,
				date,
				meal_diary
			)

	def test_abstract_rule(self, meal_collection, date, meal_diary):
		"""
		Test general properties which apply to all rules
		"""

		trivial_rule = TrivialRule()
		returned_meal_collection = trivial_rule(meal_collection, date, meal_diary)

		# Returned rule collection should be a copy, not the same instance
		assert returned_meal_collection is not meal_collection