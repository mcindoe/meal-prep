from mealprep.src.meal import Meal
from mealprep.src.meal import MealCollection
from mealprep.src.meal import MealDiary


class TestMealCollection:
    def test_initialiser(self):
        meals = (
            Meal.from_name("Spaghetti Bolognaise"),
            Meal.from_name("Sticky Chinese Pork Belly")
        )
        meal_collection = MealCollection(meals)

        # MealCollections should maintain their own copy of their meals
        assert meal_collection.meals is not meals

    def from_supported_meals(self):
        """Test that we can load meals from the project supported specification"""

        x = MealCollection.from_supported_meals()
        assert isinstance(x, MealCollection)
