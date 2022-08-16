import copy
import datetime as dt
import json
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Iterable
from typing import Optional

from mealprep.src.constants import BaseEnum
from mealprep.src.constants import MealMeat
from mealprep.src.constants import MealMetadata
from mealprep.src.constants import MealProperty
from mealprep.src.constants import MealTag
from mealprep.src.constants import Unit
from mealprep.src.ingredient import Ingredients
from mealprep.src.ingredient import IngredientQuantity
from mealprep.src.ingredient import IngredientQuantityCollection
from mealprep.src.utils import get_day_suffix
from mealprep.src.loc import DATA_DIR

MEAL_DIARY_FILEPATH = DATA_DIR / "meal_diary.json"


class Meal:
    def __init__(
        self,
        name: str,
        ingredient_quantities: IngredientQuantityCollection,
        properties: Dict[MealProperty, Any],
        tags: Optional[Iterable[MealTag]] = tuple()
    ):
        self.name = name
        self.ingredient_quantities = IngredientQuantityCollection(ingredient_quantities)

        assert isinstance(properties, dict)
        assert all(isinstance(x, MealProperty) for x in properties.keys())

        missing_properties = tuple(x for x in MealProperty if x not in properties.keys())
        if missing_properties:
            raise ValueError(f"Unspecified properties in Meal construction: {missing_properties}")

        self.metadata = properties.copy()

        for tag in MealTag:
            self.metadata[tag] = tag in tags

    @staticmethod
    def from_name(meal_name: str):
        try:
            return meal_names_to_meal_map[meal_name.upper()]
        except KeyError:
            raise ValueError(f'Could not find the meal "{meal_name}"')

    def __repr__(self) -> str:
        return f'Meal(name="{self.name}")'

    def __getitem__(self, key: MealMetadata) -> Any:
        assert isinstance(key, MealMetadata), "Key must be a MealMetadata instance in operator[]"
        return self.metadata[key]


class MealCollection:
    def __init__(self, meals: Iterable[Meal] = None):
        if meals is None:
            self.meals = tuple()
        else:
            self.meals = tuple(x for x in meals)

        assert all(isinstance(x, Meal) for x in self.meals)

    def copy(self) -> "MealCollection":
        return MealCollection(copy.copy(self.meals))

    @staticmethod
    def from_supported_meals() -> "MealCollection":
        return MealCollection(x for x in Meals.values())

    def __repr__(self) -> str:
        return str(self.meals)

    def __bool__(self) -> bool:
        return len(self.meals) > 0


class MealDiary:
    DATE_FORMAT = "%Y-%m-%d"

    @staticmethod
    def get_pretty_print_date_string(
        date: dt.date,
        include_date_number_spacing: bool = False,
        include_year: bool = False
    ) -> str:
        """
        Get a representation of a date object as, e.g., Wed 5th Jan 22.

        Args:
        include_date_number_spacing: whether to ensure that the date number
            portion of the returned string has two characters, by left-padding
            numbers less than 10 with a space
        include_year: if true, include the final two characters of the year
        """

        weekday_str = date.strftime("%A")[:3]
        date_number_str = str(date.day)
        if include_date_number_spacing and date.day < 10:
            date_number_str = " " + date_number_str
        date_number_suffix = get_day_suffix(date.day)
        month_str = date.strftime("%B")[:3]

        ret = f"{weekday_str} {date_number_str}{date_number_suffix} {month_str}"

        if include_year:
            ret += f" {date.strftime('%Y')}"

        return ret

    def __init__(self, meal_diary: Dict[dt.date, Meal] = None):
        if meal_diary is not None:
            assert isinstance(meal_diary, dict)

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

    def get_pretty_print_string(self):
        include_date_number_spacing = any(x.day > 10 for x in self.dates)
        include_year = len(set(x.year for x in self.dates)) > 1

        lines = []
        for date, meal in self.items():
            date_str = self.get_pretty_print_date_string(date, include_date_number_spacing, include_year)
            lines.append(f"{date_str}: {meal.name}")

        return "\n".join(lines)


class Meals(BaseEnum):
    CHILLI_CHICKEN_THIGHS_WITH_CHERRY_TOMATOES = Meal(
        name="Chilli Chicken Thighs with Cherry Tomatoes",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.CHERRY_TOMATO, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.CHICKEN_THIGH, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.GARLIC_CLOVE, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.OLIVE_OIL, Unit.BOOL, True),
            IngredientQuantity(Ingredients.RED_CHILLI, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.RICE, Unit.GRAM, 200),
        ),
        properties={
            MealProperty.MEAT: MealMeat.CHICKEN
        }
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
        ),
        properties={
            MealProperty.MEAT: MealMeat.BEEF
        }
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
        ),
        properties={
            MealProperty.MEAT: MealMeat.CHICKEN
        },
        tags=(
            MealTag.PASTA,
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
        ),
        properties={
            MealProperty.MEAT: MealMeat.BEEF
        },
        tags=(
            MealTag.PASTA,
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
        ),
        properties={
            MealProperty.MEAT: MealMeat.PORK
        }
    )


meal_names_to_meal_map = {x.value.name.upper(): x.value for x in Meals}
