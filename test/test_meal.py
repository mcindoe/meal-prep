import datetime as dt
import pytest

from mealprep.src.constants import MealMeat
from mealprep.src.constants import MealProperty
from mealprep.src.constants import MealTag
from mealprep.src.constants import Unit
from mealprep.src.ingredient import IngredientQuantity
from mealprep.src.ingredient import IngredientQuantityCollection
from mealprep.src.ingredient import Ingredients
from mealprep.src.meal import Meal
from mealprep.src.meal import MealCollection
from mealprep.src.meal import MealDiary


class TestMeal:
    def test_initialiser_errors(self):
        # Name is not a string
        with pytest.raises(TypeError):
            Meal(
                name=42,
                ingredient_quantities=(
                    IngredientQuantity(Ingredients.BAY_LEAVES, Unit.BOOL, True),
                    IngredientQuantity(Ingredients.CARROT, Unit.NUMBER, 1),
                ),
                properties={},
                tags=(MealTag.PASTA,),
            )

        # Properties not a dictionary
        with pytest.raises(TypeError):
            Meal(
                name="Meal Name",
                ingredient_quantities=(
                    IngredientQuantity(Ingredients.BAY_LEAVES, Unit.BOOL, True),
                    IngredientQuantity(Ingredients.CARROT, Unit.NUMBER, 1),
                ),
                properties=(MealMeat.BEEF,),
                tags=(MealTag.PASTA,),
            )

        # Properties contains non-properties
        with pytest.raises(TypeError):
            Meal(
                name="Meal Name",
                ingredient_quantities=(
                    IngredientQuantity(Ingredients.BAY_LEAVES, Unit.BOOL, True),
                    IngredientQuantity(Ingredients.CARROT, Unit.NUMBER, 1),
                ),
                properties=({"Meat": "Beef"}),
                tags=(MealTag.PASTA,),
            )

        # Missing properties
        with pytest.raises(ValueError):
            Meal(
                name="Meal Name",
                ingredient_quantities=(
                    IngredientQuantity(Ingredients.BAY_LEAVES, Unit.BOOL, True),
                    IngredientQuantity(Ingredients.CARROT, Unit.NUMBER, 1),
                ),
                properties={},
                tags=(MealTag.PASTA,),
            )

        # Ingredient Quantities contains non-Ingredients
        with pytest.raises(TypeError):
            Meal(
                name="Meal Name",
                ingredient_quantities=(
                    "300g of Carrot",
                ),
                properties={
                    MealProperty.MEAT: MealMeat.BEEF
                },
                tags=(MealTag.PASTA,),
            )

        # Tags argument contains non-Tags
        with pytest.raises(ValueError):
            Meal(
                name="Meal Name",
                ingredient_quantities=(
                    IngredientQuantity(Ingredients.BAY_LEAVES, Unit.BOOL, True),
                    IngredientQuantity(Ingredients.CARROT, Unit.NUMBER, 1),
                ),
                properties={
                    MealProperty.MEAT: MealMeat.BEEF
                },
                tags=("PASTA",),
            )

        # Ingredient quantities contains more than one entry of the same ingredient
        with pytest.raises(ValueError):
            Meal(
                name="Meal Name",
                ingredient_quantities=(
                    IngredientQuantity(Ingredients.BAY_LEAVES, Unit.BOOL, True),
                    IngredientQuantity(Ingredients.CARROT, Unit.NUMBER, 1),
                    IngredientQuantity(Ingredients.CARROT, Unit.GRAM, 100),
                ),
                properties={
                    MealProperty.MEAT: MealMeat.BEEF
                },
                tags=(MealTag.PASTA,),
            )

    def test_getters(self):
        x = Meal(
            name="Meal Name",
            ingredient_quantities=(
                IngredientQuantity(Ingredients.BAY_LEAVES, Unit.BOOL, True),
                IngredientQuantity(Ingredients.CARROT, Unit.NUMBER, 1),
            ),
            properties={
                MealProperty.MEAT: MealMeat.BEEF
            },
            tags=(MealTag.PASTA,)
        )

        assert x.name == "Meal Name"
        assert isinstance(x.ingredient_quantities, IngredientQuantityCollection)
        assert x[MealProperty.MEAT] is MealMeat.BEEF
        assert x[MealTag.PASTA]
        assert not x[MealTag.VEGETARIAN]

        chinese_pork_belly = Meal.from_name("Sticky Chinese Pork Belly")
        assert chinese_pork_belly[MealProperty.MEAT] is MealMeat.PORK
        assert not chinese_pork_belly[MealTag.VEGETARIAN]

    def test_init_from_single_tag(self):
        # Construction from a single tag
        x = Meal(
            name="Meal Name",
            ingredient_quantities=(
                IngredientQuantity(Ingredients.BAY_LEAVES, Unit.BOOL, True),
                IngredientQuantity(Ingredients.CARROT, Unit.NUMBER, 1),
            ),
            properties={
                MealProperty.MEAT: MealMeat.BEEF
            },
            tags=MealTag.PASTA
        )

        assert isinstance(x, Meal)

    def test_construction_from_name(self):
        meal = Meal.from_name("Spaghetti Bolognese")

        assert isinstance(meal, Meal)
        assert meal[MealProperty.MEAT] is MealMeat.BEEF


class TestMealCollection:
    @pytest.fixture()
    def meals(self):
        yield (
            Meal.from_name("Spaghetti Bolognese"),
            Meal.from_name("Sticky Chinese Pork Belly"),
        )

    @pytest.fixture()
    def meal_collection(self, meals):
        yield MealCollection(meals)

    def test_initialiser(self, meals, meal_collection):
        # MealCollections should maintain their own copy of their meals
        assert meal_collection.meals is not meals

        # One of the collection is not a Meal
        with pytest.raises(TypeError):
            MealCollection(meals + ("Lasagne",))

    def test_properties(self, meal_collection):
        assert len(meal_collection) == 2
        assert bool(meal_collection)

        empty_collection = MealCollection()
        assert not bool(empty_collection)
        assert not empty_collection

    def test_indexing(self, meals, meal_collection):
        assert meal_collection[0] is meals[0]
        assert meal_collection[1] is meals[1]

    def test_eq(self, meals):
        mc1 = MealCollection((meals[0], meals[1]))
        mc2 = MealCollection((meals[1], meals[0]))

        assert mc1 == mc2
        assert mc1 != MealCollection((meals[0],))


class TestMealDiary:
    @pytest.fixture()
    def meal_diary_dict(self):
        yield {
            dt.date(2022, 1, 1): Meal.from_name("Spaghetti Bolognese"),
            dt.date(2022, 1, 10): Meal.from_name("Lasagne"),
            dt.date(2022, 1, 11): Meal.from_name("Kedgeree"),
        }

    @pytest.fixture()
    def meal_diary(self, meal_diary_dict):
        yield MealDiary(meal_diary_dict)

    def test_initialiser(self, meal_diary_dict, meal_diary):
        assert isinstance(meal_diary, MealDiary)

        # MealDiaries should create a copy of the passed dictionary
        assert meal_diary.meal_diary is not meal_diary_dict

    def test_initialiser_errors(self):
        # Keys are not all datetime.dates
        with pytest.raises(TypeError):
            MealDiary({
                "2022-01-01": Meal.from_name("Spaghetti Bolognese"),
            })

        # Values are not all Meals
        with pytest.raises(TypeError):
            MealDiary({
                dt.date(2022, 1, 1): "Spaghetti Bolognese",
            })

    def test_copy(self, meal_diary):
        assert meal_diary == meal_diary.copy()
        assert meal_diary is not meal_diary.copy()

    def test_indexing(self, meal_diary):
        with pytest.raises(TypeError):
            meal_diary["2022-01-01"]

        assert meal_diary[dt.date(2022, 1, 1)] == Meal.from_name("Spaghetti Bolognese")

        altered_diary = meal_diary.copy()

        # Setting with a non-date key is not allowed
        with pytest.raises(TypeError):
            altered_diary["2022-01-01"] = Meal.from_name("Spaghetti Bolognese")

        # Setting with a non-meal value is not allowed
        with pytest.raises(TypeError):
            altered_diary[dt.date(2022, 1, 1)] = "Spaghetti Bolognese"

        altered_diary[dt.date(2022, 2, 1)] = Meal.from_name("Sticky Chinese Pork Belly")
        assert len(altered_diary) == 4
        assert dt.date(2022, 2, 1) in altered_diary.dates

    def test_loading_project_diary(self):
        project_diary = MealDiary.from_project_diary()
        assert isinstance(project_diary, MealDiary)

    def test_upsert(self, meal_diary):
        addition = MealDiary({
            dt.date(2022, 2, 1): Meal.from_name("Sticky Chinese Pork Belly")
        })
        altered_diary = meal_diary.copy()

        assert altered_diary.upsert(addition).meal_diary is not altered_diary.meal_diary
        assert dt.date(2022, 2, 1) in altered_diary.upsert(addition).dates

    def test_difference(self, meal_diary):
        overlapping_diary = MealDiary({
            dt.date(2022, 1, 1): Meal.from_name("Spaghetti Bolognese"),
        })
        difference_diary = meal_diary.difference(overlapping_diary)

        assert len(difference_diary) == 2
        assert dt.date(2022, 1, 1) not in difference_diary.dates
        assert dt.date(2022, 1, 10) in difference_diary.dates
        assert Meal.from_name("Spaghetti Bolognese") not in difference_diary.meals
        assert Meal.from_name("Kedgeree") in difference_diary.meals

    def test_filter_by_time_delta(self, meal_diary):
        expected_diary = MealDiary({
            dt.date(2022, 1, 10): Meal.from_name("Lasagne"),
            dt.date(2022, 1, 11): Meal.from_name("Kedgeree")
        })
        observed_diary = meal_diary.filter_by_time_delta(dt.date(2022, 1, 10), dt.timedelta(days=1))

        assert expected_diary == observed_diary

    def test_filter_dates(self, meal_diary):
        observed_diary_1 = meal_diary.filter_dates(
            min_date=dt.date(2022, 1, 1),
            max_date=dt.date(2022, 1, 11)
        )
        expected_diary_1 = MealDiary({
            dt.date(2022, 1, 1): Meal.from_name("Spaghetti Bolognese"),
            dt.date(2022, 1, 10): Meal.from_name("Lasagne"),
        })

        observed_diary_2 = meal_diary.filter_dates(min_date=dt.date(2022, 1, 1))
        expected_diary_2 = MealDiary({
            dt.date(2022, 1, 1): Meal.from_name("Spaghetti Bolognese"),
            dt.date(2022, 1, 10): Meal.from_name("Lasagne"),
            dt.date(2022, 1, 11): Meal.from_name("Kedgeree")
        })

        observed_diary_3 = meal_diary.filter_dates(min_date=dt.date(2022, 1, 5))
        expected_diary_3 = MealDiary({
            dt.date(2022, 1, 10): Meal.from_name("Lasagne"),
            dt.date(2022, 1, 11): Meal.from_name("Kedgeree")
        })

        assert observed_diary_1 == expected_diary_1
        assert observed_diary_2 == expected_diary_2
        assert observed_diary_3 == expected_diary_3

        with pytest.raises(TypeError):
            meal_diary.filter_dates(start_date="2022-01-01")

        with pytest.raises(TypeError):
            meal_diary.filter_dates(start_date=dt.date(2022, 1, 1), end_date="2022-02-01")

    def test_except_dates(self, meal_diary):
        expected_diary = MealDiary({
            dt.date(2022, 1, 1): Meal.from_name("Spaghetti Bolognese"),
            dt.date(2022, 1, 11): Meal.from_name("Kedgeree")
        })

        # Should be able to exclude either a single date or an iterable of dates
        observed_diary_1 = meal_diary.except_dates(dt.date(2022, 1, 10),)
        observed_diary_2 = meal_diary.except_dates(dt.date(2022, 1, 10))

        assert observed_diary_1 == observed_diary_2
        assert expected_diary == observed_diary_1

        with pytest.raises(TypeError):
            # Passed dates must be datetime.dates
            meal_diary.except_dates("2022-01-01")
