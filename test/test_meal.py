import datetime as dt
import unittest

from mealprep.constants import MealMeat, MealProperty, MealTag, Unit
from mealprep.ingredient import Ingredient, IngredientQuantity, IngredientQuantityCollection
from mealprep.meal import Meal
from mealprep.meal_collection import MealCollection
from mealprep.meal_diary import MealDiary
from mealprep.recipe.reading import get_meal_from_name


class TestMeal(unittest.TestCase):
    def test_initialiser_errors(self):
        # Name is not a string
        with self.assertRaises(TypeError):
            Meal(
                name=42,
                ingredient_quantities=IngredientQuantityCollection(
                    (
                        IngredientQuantity(Ingredient.from_name("Bay Leaves"), Unit.BOOL, True),
                        IngredientQuantity(Ingredient.from_name("Carrot"), Unit.NUMBER, 1),
                    )
                ),
                properties={},
                tags=(MealTag.PASTA,),
            )

        # Properties not a dictionary
        with self.assertRaises(TypeError):
            Meal(
                name="Meal Name",
                ingredient_quantities=IngredientQuantityCollection(
                    (
                        IngredientQuantity(Ingredient.from_name("Bay Leaves"), Unit.BOOL, True),
                        IngredientQuantity(Ingredient.from_name("Carrot"), Unit.NUMBER, 1),
                    )
                ),
                properties=(MealMeat.BEEF,),
                tags=(MealTag.PASTA,),
            )

        # Properties contains non-properties
        with self.assertRaises(TypeError):
            Meal(
                name="Meal Name",
                ingredient_quantities=IngredientQuantityCollection(
                    (
                        IngredientQuantity(Ingredient.from_name("Bay Leaves"), Unit.BOOL, True),
                        IngredientQuantity(Ingredient.from_name("Carrot"), Unit.NUMBER, 1),
                    )
                ),
                properties=({"Meat": "Beef"}),
                tags=(MealTag.PASTA,),
            )

        # Missing properties
        with self.assertRaises(ValueError):
            Meal(
                name="Meal Name",
                ingredient_quantities=IngredientQuantityCollection(
                    (
                        IngredientQuantity(Ingredient.from_name("Bay Leaves"), Unit.BOOL, True),
                        IngredientQuantity(Ingredient.from_name("Carrot"), Unit.NUMBER, 1),
                    )
                ),
                properties={},
                tags=(MealTag.PASTA,),
            )

        # Tags argument contains non-Tags
        with self.assertRaises(ValueError):
            Meal(
                name="Meal Name",
                ingredient_quantities=IngredientQuantityCollection(
                    (
                        IngredientQuantity(Ingredient.from_name("Bay Leaves"), Unit.BOOL, True),
                        IngredientQuantity(Ingredient.from_name("Carrot"), Unit.NUMBER, 1),
                    )
                ),
                properties={MealProperty.MEAT: MealMeat.BEEF},
                tags=("PASTA",),
            )

        # Ingredient quantities contains more than one entry of the same ingredient
        with self.assertRaises(ValueError):
            Meal(
                name="Meal Name",
                ingredient_quantities=IngredientQuantityCollection(
                    (
                        IngredientQuantity(Ingredient.from_name("Bay Leaves"), Unit.BOOL, True),
                        IngredientQuantity(Ingredient.from_name("Carrot"), Unit.NUMBER, 1),
                        IngredientQuantity(Ingredient.from_name("Carrot"), Unit.GRAM, 100),
                    )
                ),
                properties={MealProperty.MEAT: MealMeat.BEEF},
                tags=(MealTag.PASTA,),
            )

    def test_getters(self):
        x = Meal(
            name="Meal Name",
            ingredient_quantities=IngredientQuantityCollection(
                (
                    IngredientQuantity(Ingredient.from_name("Bay Leaves"), Unit.BOOL, True),
                    IngredientQuantity(Ingredient.from_name("Carrot"), Unit.NUMBER, 1),
                )
            ),
            properties={MealProperty.MEAT: MealMeat.BEEF},
            tags=(MealTag.PASTA,),
        )

        self.assertEqual(x.name, "Meal Name")
        self.assertIsInstance(x.ingredient_quantities, IngredientQuantityCollection)
        self.assertIs(x[MealProperty.MEAT], MealMeat.BEEF)
        self.assertTrue(x[MealTag.PASTA])
        self.assertFalse(x[MealTag.VEGETARIAN])

        chinese_pork_belly = get_meal_from_name("Sticky Chinese Pork Belly")
        self.assertIs(chinese_pork_belly[MealProperty.MEAT], MealMeat.PORK)
        self.assertFalse(chinese_pork_belly[MealTag.VEGETARIAN])

    def test_init_from_single_tag(self):
        # Construction from a single tag
        x = Meal(
            name="Meal Name",
            ingredient_quantities=IngredientQuantityCollection(
                (
                    IngredientQuantity(Ingredient.from_name("Bay Leaves"), Unit.BOOL, True),
                    IngredientQuantity(Ingredient.from_name("Carrot"), Unit.NUMBER, 1),
                )
            ),
            properties={MealProperty.MEAT: MealMeat.BEEF},
            tags=MealTag.PASTA,
        )

        self.assertIsInstance(x, Meal)

    def test_construction_from_name(self):
        meal = get_meal_from_name("Spaghetti Bolognese")

        self.assertIsInstance(meal, Meal)
        self.assertIs(meal[MealProperty.MEAT], MealMeat.BEEF)


class TestMealCollection(unittest.TestCase):
    meals = (
        get_meal_from_name("Spaghetti Bolognese"),
        get_meal_from_name("Sticky Chinese Pork Belly"),
    )

    meal_collection = MealCollection(meals)

    def test_initialiser(self):
        # MealCollections should maintain their own copy of their meals
        self.assertIsNot(self.meal_collection.meals, self.meals)

        # One of the collection is not a Meal
        with self.assertRaises(TypeError):
            MealCollection(self.meals + ("Lasagne",))

    def test_properties(self):
        self.assertEqual(len(self.meal_collection), 2)
        self.assertTrue(bool(self.meal_collection))

        empty_collection = MealCollection()
        self.assertFalse(bool(empty_collection))
        self.assertFalse(empty_collection)

    def test_indexing(self):
        self.assertIs(self.meal_collection[0], self.meals[0])
        self.assertIs(self.meal_collection[1], self.meals[1])

    def test_eq(self):
        mc1 = MealCollection((self.meals[0], self.meals[1]))
        mc2 = MealCollection((self.meals[1], self.meals[0]))

        self.assertEqual(mc1, mc2)
        self.assertNotEqual(mc1, MealCollection((self.meals[0],)))


class TestMealDiary(unittest.TestCase):
    meal_diary_dict = {
        dt.date(2022, 1, 1): get_meal_from_name("Spaghetti Bolognese"),
        dt.date(2022, 1, 10): get_meal_from_name("Lasagne"),
        dt.date(2022, 1, 11): get_meal_from_name("Kedgeree"),
    }

    meal_diary = MealDiary(meal_diary_dict)

    def test_initialiser(self):
        self.assertIsInstance(self.meal_diary, MealDiary)

        # MealDiaries should create a copy of the passed dictionary
        self.assertIsNot(self.meal_diary.meal_diary, self.meal_diary_dict)

    def test_initialiser_errors(self):
        # Keys are not all datetime.dates
        with self.assertRaises(TypeError):
            MealDiary(
                {
                    "2022-01-01": get_meal_from_name("Spaghetti Bolognese"),
                }
            )

        # Values are not all Meals
        with self.assertRaises(TypeError):
            MealDiary(
                {
                    dt.date(2022, 1, 1): "Spaghetti Bolognese",
                }
            )

    def test_copy(self):
        self.assertEqual(self.meal_diary, self.meal_diary.copy())
        self.assertIsNot(self.meal_diary, self.meal_diary.copy())

    def test_indexing(self):
        with self.assertRaises(TypeError):
            self.meal_diary["2022-01-01"]

        self.assertEqual(
            self.meal_diary[dt.date(2022, 1, 1)], get_meal_from_name("Spaghetti Bolognese")
        )

        altered_diary = self.meal_diary.copy()

        # Setting with a non-date key is not allowed
        with self.assertRaises(TypeError):
            altered_diary["2022-01-01"] = get_meal_from_name("Spaghetti Bolognese")

        # Setting with a non-meal value is not allowed
        with self.assertRaises(TypeError):
            altered_diary[dt.date(2022, 1, 1)] = "Spaghetti Bolognese"

        altered_diary[dt.date(2022, 2, 1)] = get_meal_from_name("Sticky Chinese Pork Belly")
        self.assertEqual(len(altered_diary), 4)
        self.assertIn(dt.date(2022, 2, 1), altered_diary.dates)

    def test_loading_project_diary(self):
        project_diary = MealDiary.from_project_diary()
        self.assertIsInstance(project_diary, MealDiary)

    def test_upsert(self):
        addition = MealDiary({dt.date(2022, 2, 1): get_meal_from_name("Sticky Chinese Pork Belly")})
        altered_diary = self.meal_diary.copy()

        self.assertIsNot(altered_diary.upsert(addition).meal_diary, altered_diary.meal_diary)
        self.assertIn(dt.date(2022, 2, 1), altered_diary.upsert(addition).dates)

    def test_difference(self):
        overlapping_diary = MealDiary(
            {
                dt.date(2022, 1, 1): get_meal_from_name("Spaghetti Bolognese"),
            }
        )
        difference_diary = self.meal_diary.difference(overlapping_diary)

        self.assertEqual(len(difference_diary), 2)
        self.assertNotIn(dt.date(2022, 1, 1), difference_diary.dates)
        self.assertIn(dt.date(2022, 1, 10), difference_diary.dates)
        self.assertNotIn(get_meal_from_name("Spaghetti Bolognese"), difference_diary.meals)
        self.assertIn(get_meal_from_name("Kedgeree"), difference_diary.meals)

    def test_filter_by_time_delta(self):
        expected_diary = MealDiary(
            {
                dt.date(2022, 1, 10): get_meal_from_name("Lasagne"),
                dt.date(2022, 1, 11): get_meal_from_name("Kedgeree"),
            }
        )
        observed_diary = self.meal_diary.filter_by_time_delta(
            dt.date(2022, 1, 10), dt.timedelta(days=1)
        )

        self.assertEqual(expected_diary, observed_diary)

    def test_filter_dates(self):
        observed_diary_1 = self.meal_diary.filter_dates(
            min_date=dt.date(2022, 1, 1), max_date=dt.date(2022, 1, 11)
        )
        expected_diary_1 = MealDiary(
            {
                dt.date(2022, 1, 1): get_meal_from_name("Spaghetti Bolognese"),
                dt.date(2022, 1, 10): get_meal_from_name("Lasagne"),
            }
        )

        observed_diary_2 = self.meal_diary.filter_dates(min_date=dt.date(2022, 1, 1))
        expected_diary_2 = MealDiary(
            {
                dt.date(2022, 1, 1): get_meal_from_name("Spaghetti Bolognese"),
                dt.date(2022, 1, 10): get_meal_from_name("Lasagne"),
                dt.date(2022, 1, 11): get_meal_from_name("Kedgeree"),
            }
        )

        observed_diary_3 = self.meal_diary.filter_dates(min_date=dt.date(2022, 1, 5))
        expected_diary_3 = MealDiary(
            {
                dt.date(2022, 1, 10): get_meal_from_name("Lasagne"),
                dt.date(2022, 1, 11): get_meal_from_name("Kedgeree"),
            }
        )

        self.assertEqual(observed_diary_1, expected_diary_1)
        self.assertEqual(observed_diary_2, expected_diary_2)
        self.assertEqual(observed_diary_3, expected_diary_3)

        with self.assertRaises(TypeError):
            self.meal_diary.filter_dates(start_date="2022-01-01")

        with self.assertRaises(TypeError):
            self.meal_diary.filter_dates(start_date=dt.date(2022, 1, 1), end_date="2022-02-01")

    def test_except_dates(self):
        expected_diary = MealDiary(
            {
                dt.date(2022, 1, 1): get_meal_from_name("Spaghetti Bolognese"),
                dt.date(2022, 1, 11): get_meal_from_name("Kedgeree"),
            }
        )

        # Should be able to exclude either a single date or an iterable of dates
        observed_diary_1 = self.meal_diary.except_dates(
            dt.date(2022, 1, 10),
        )
        observed_diary_2 = self.meal_diary.except_dates(dt.date(2022, 1, 10))

        self.assertEqual(observed_diary_1, observed_diary_2)
        self.assertEqual(expected_diary, observed_diary_1)

        with self.assertRaises(TypeError):
            # Passed dates must be datetime.dates
            self.meal_diary.except_dates("2022-01-01")
