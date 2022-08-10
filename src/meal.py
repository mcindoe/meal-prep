from copy import copy
import datetime as dt
import json
from pathlib import Path
from typing import Dict
from typing import Iterable

from mealprep.src.constants import BaseEnum
from mealprep.src.constants import Unit
from mealprep.src.ingredient import Ingredients
from mealprep.src.ingredient_quantity import IngredientQuantity, IngredientQuantityCollection

MEALPREP_TOPDIR = Path("/home/conor/Programming/mealprep")
DATA_DIR = MEALPREP_TOPDIR / "data"
MEAL_HISTORY_FILEPATH = DATA_DIR / "meal_history.json"


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
    def __init__(self, meals: Iterable[Meal]):
        self.meals = tuple(x for x in meals)

        # TODO: Note that these asserts need to be after the object is constructed,
        # since otherwise generator expressions are exhausted by the time it comes to initialise
        assert all(isinstance(x, Meal) for x in self.meals)

    @staticmethod
    def from_supported_meals() -> "MealCollection":
        return MealCollection(x for x in Meals.values())

    def __repr__(self) -> str:
        return str(self.meals)


class MealDiary:
    DATE_FORMAT = "%Y-%m-%d"

    def __init__(self, meal_diary: Dict[dt.date, Meal]):
        assert isinstance(meal_diary, dict)
        assert all(isinstance(x, dt.date) for x in meal_diary.keys())
        assert all(isinstance(x, Meal) for x in meal_diary.values())

        self.meal_diary = copy(meal_diary)

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

    def to_history_file(self) -> None:
        self.to_file(MEAL_HISTORY_FILEPATH)

    @staticmethod
    def from_history_file() -> None:
        return MealDiary.from_file(MEAL_HISTORY_FILEPATH)

    def upsert(self, other: "MealDiary") -> "MealDiary":
        return MealDiary(self.meal_diary | other.meal_diary)


class Meals(BaseEnum):
    EXAMPLE = Meal(
        "Example",
        (IngredientQuantity(Ingredients.CARROT.value, Unit.GRAM, 100),)
    )
