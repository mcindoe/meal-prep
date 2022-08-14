import copy
import datetime as dt
import json
from pathlib import Path
from typing import Dict
from typing import Iterable

from mealprep.src.constants import BaseEnum
from mealprep.src.constants import Unit
from mealprep.src.ingredient import Ingredients
from mealprep.src.ingredient import IngredientQuantity
from mealprep.src.ingredient import IngredientQuantityCollection
from mealprep.src.loc import DATA_DIR

MEAL_DIARY_FILEPATH = DATA_DIR / "meal_diary.json"


class Meal:
    def __init__(self, name: str, ingredient_quantities: IngredientQuantityCollection):
        self.name = name
        self.ingredient_quantities = IngredientQuantityCollection(ingredient_quantities)

    @staticmethod
    def from_name(meal_name: str):
        for meal in Meals.values():
            if meal.name.lower() == meal_name.lower():
                return meal
        raise ValueError(f'Could not find the meal "{meal_name}"')

    def __repr__(self) -> str:
        return f'Meal(name="{self.name}")'


class MealCollection:
    def __init__(self, meals: Iterable[Meal] = None):
        if meals is None:
            self.meals = tuple()
        else:
            self.meals = tuple(x for x in meals)

        # TODO: Note that these asserts need to be after the object is constructed,
        # since otherwise generator expressions are exhausted by the time it comes to initialise
        assert all(isinstance(x, Meal) for x in self.meals)

    def copy(self) -> "MealCollection":
        return MealCollection(copy.deepcopy(self.meals))

    @staticmethod
    def from_supported_meals() -> "MealCollection":
        return MealCollection(x for x in Meals.values())

    def __repr__(self) -> str:
        return str(self.meals)

    def __bool__(self) -> bool:
        return len(self.meals) > 0


class MealDiary:
    DATE_FORMAT = "%Y-%m-%d"

    def __init__(self, meal_diary: Dict[dt.date, Meal] = None):
        assert isinstance(meal_diary, (None, dict))

        if meal_diary is None:
            self.meal_diary = dict()
        else:
            self.meal_diary = meal_diary.copy()

        assert all(isinstance(x, dt.date) for x in self.meal_diary.keys())
        assert all(isinstance(x, Meal) for x in self.meal_diary.values())

    def copy(self):
        return MealDiary(copy.deepcopy(self.meal_diary))

    def __getitem__(self, date: dt.date) -> Meal:
        if not isinstance(date, dt.date):
            raise ValueError("Key must be date in MealDiary.__getitem__")

        return self.meal_diary[date]

    def __setitem__(self, date: dt.date, meal: Meal) -> None:
        if not isinstance(date, dt.date):
            raise ValueError("Key must be date in MealDiary.__getitem__")
        if not isinstance(meal, Meal):
            raise ValueError("value must be a Meal in MealDiary.__getitem__")

        self.meal_diary[date] = meal

    @property
    def dates(self):
        return tuple(self.meal_diary.keys())

    @property
    def meals(self):
        return tuple(self.meal_diary.values())

    def items(self):
        return self.meal_diary.items()

    def get_representation(self):
        """
        Represent the instance as a dictionary mapping date strings
        to meal names
        """
        ret = {
            date.strftime(MealDiary.DATE_FORMAT): meal.name
            for date, meal in self.items()
        }
        return dict(sorted(ret.items()))

    def __str__(self):
        return str(self.get_representation())

    def to_file(self, file_path: Path):
        with open(file_path, "w+") as fp:
            json.dump(self.get_representation(), fp, indent=2)

    @staticmethod
    def from_file(file_path: Path) -> "MealDiary":
        try:
            with open(file_path, "r") as fp:
                dict_representation = json.load(fp)
        except FileNotFoundError:
            raise ValueError(f'Specified file "{file_path}" could not be found')
        except json.decoder.JSONDecodeError:
            raise ValueError(f'Specified file "{file_path}" could not be parsed into JSON')

        return MealDiary({
            dt.datetime.strptime(date_string, MealDiary.DATE_FORMAT).date(): Meal.from_name(meal_name)
            for date_string, meal_name in dict_representation.items()
        })

    def to_project_diary(self) -> None:
        self.to_file(MEAL_DIARY_FILEPATH)

    @staticmethod
    def from_project_diary() -> None:
        return MealDiary.from_file(MEAL_DIARY_FILEPATH)

    def upsert(self, other: "MealDiary") -> "MealDiary":
        return MealDiary(self.meal_diary | other.meal_diary)

    def difference(self, other: "MealDiary") -> "MealDiary":
        return MealDiary({
            date: meal
            for date, meal in self.meal_diary.copy()
            if date not in other.meal_diary.keys()
        })

    def filter_by_time_delta(self, date: dt.date, time_delta: dt.timedelta):
        return MealDiary({
            meal_date: meal
            for meal_date, meal in self.items()
            if abs(meal_date - date) <= time_delta
        })


class Meals(BaseEnum):
    CHILLI_CHICKEN_THIGS_WITH_CHERRY_TOMATOES = Meal(
        name="Chilli Chicken Thigs with Cherry Tomatoes",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.CHERRY_TOMATO, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.CHICKEN_THIGH, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.GARLIC_CLOVE, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.OLIVE_OIL, Unit.BOOL, True),
            IngredientQuantity(Ingredients.RED_CHILLI, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.RICE, Unit.GRAM, 200),
        )
    )
    CHILLI_CON_CARNE = Meal(
        name="Chilli con Carne",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.BEEF_MINCE, Unit.GRAM, 900),
            IngredientQuantity(Ingredients.CARROT, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.CELERY, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.CHOPPED_TOMATO, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.FRESH_CHILLI, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.GARLIC_CLOVE, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.KIDNEY_BEAN, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.ONION, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.RICE, Unit.GRAM, 250),
            IngredientQuantity(Ingredients.TOMATO_PUREE, Unit.BOOL, True),
        )
    )
    PASTA_WITH_CHICKEN_AND_SUNDRIED_TOMATOES = Meal(
        name="Pasta with Chicken and Sundried Tomatoes",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.BABY_SPINACH, Unit.GRAM, 200),
            IngredientQuantity(Ingredients.CAYENNE_PEPPER, Unit.BOOL, True),
            IngredientQuantity(Ingredients.CHICKEN_BREAST, Unit.GRAM, 700),
            IngredientQuantity(Ingredients.CHICKEN_STOCK, Unit.GRAM, 250),
            IngredientQuantity(Ingredients.CREAM, Unit.GRAM, 250),
            IngredientQuantity(Ingredients.GARLIC_CLOVE, Unit.NUMBER, 3),
            IngredientQuantity(Ingredients.MOZARELLA_CHEESE, Unit.GRAM, 100),
            IngredientQuantity(Ingredients.PARMEZAN_CHEESE, Unit.GRAM, 100),
            IngredientQuantity(Ingredients.PENNE_PASTA, Unit.GRAM, 300),
            IngredientQuantity(Ingredients.SUNDRIED_TOMATOES, Unit.GRAM, 750),
        )
    )
    SPAGHETTI_BOLOGNAISE = Meal(
        name="Spaghetti Bolognaise",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.BAY_LEAVES, Unit.BOOL, True),
            IngredientQuantity(Ingredients.BAY_LEAVES, Unit.GRAM, 500),
            IngredientQuantity(Ingredients.CARROT, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.CELERY, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.CHOPPED_TOMATO, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.GARLIC_CLOVE, Unit.NUMBER, 3),
            IngredientQuantity(Ingredients.MIXED_HERBS, Unit.BOOL, True),
            IngredientQuantity(Ingredients.ONION, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.OREGANO, Unit.BOOL, True),
            IngredientQuantity(Ingredients.PARMEZAN_CHEESE, Unit.BOOL, True),
            IngredientQuantity(Ingredients.PORK_MINCE, Unit.GRAM, 500),
            IngredientQuantity(Ingredients.SPAGHETTI, Unit.BOOL, True),
            IngredientQuantity(Ingredients.TOMATO_PUREE, Unit.BOOL, True),
        )
    )
    STICKY_CHINESE_PORK_BELLY = Meal(
        name="Sticky Chinese Pork Belly",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.BROWN_SUGAR, Unit.BOOL, True),
            IngredientQuantity(Ingredients.CASTER_SUGAR, Unit.BOOL, True),
            IngredientQuantity(Ingredients.CHICKEN_STOCK, Unit.GRAM, 1000),
            IngredientQuantity(Ingredients.DARK_SOY_SAUCE, Unit.BOOL, True),
            IngredientQuantity(Ingredients.GARLIC_CLOVE, Unit.NUMBER, 3),
            IngredientQuantity(Ingredients.GINGER, Unit.BOOL, True),
            IngredientQuantity(Ingredients.HONEY, Unit.BOOL, True),
            IngredientQuantity(Ingredients.LEMONGRASS_PASTE, Unit.BOOL, True),
            IngredientQuantity(Ingredients.PORK_BELLY_SLICE, Unit.GRAM, 1000),
            IngredientQuantity(Ingredients.RED_CHILLI, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.RICE_WINE, Unit.BOOL, True),
            IngredientQuantity(Ingredients.RICE, Unit.GRAM, 500),
            IngredientQuantity(Ingredients.VEGETABLE_OIL, Unit.BOOL, True),
        )
    )
