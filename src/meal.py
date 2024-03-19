from __future__ import annotations

import collections
from collections.abc import Iterable
import copy
import datetime as dt
import json
from pathlib import Path
from typing import Any, Optional, Tuple, Union

from mealprep.src.basic_iterator import BasicIterator
from mealprep.src.constants import (
    BaseEnum,
    MealMeat,
    MealMetadata,
    MealProperty,
    MealTag,
    Unit,
)
from mealprep.src.ingredient import (
    IngredientQuantity,
    IngredientQuantityCollection,
    Ingredients,
)
from mealprep.src.loc import DATA_DIR
from mealprep.src.utils import get_pretty_print_date_string

PROJECT_DIARY_FILENAME = "meal_diary.json"
PROJECT_DIARY_FILEPATH = DATA_DIR / PROJECT_DIARY_FILENAME


class Meal:
    def __init__(
        self,
        name: str,
        ingredient_quantities: IngredientQuantityCollection,
        properties: dict[MealProperty, Any],
        tags: Optional[Union[MealTag, Iterable[MealTag]]] = tuple(),
    ):
        self.name = name
        self.ingredient_quantities = IngredientQuantityCollection(ingredient_quantities)

        if not isinstance(name, str):
            raise TypeError("'name' argument must be a string in Meal init")

        if not isinstance(properties, dict):
            raise TypeError("'properties' argument must be a dict in Meal init")

        if not all(isinstance(x, MealProperty) for x in properties):
            raise TypeError("All keys in 'properties' dictionary must be MealProperties")

        missing_properties = tuple(x for x in MealProperty if x not in properties.keys())
        if missing_properties:
            raise ValueError(f"Unspecified properties in Meal construction: {missing_properties}")

        # There should not be more than one entry of a given ingredient
        # in the passed ingredient_quantities collection
        if ingredient_quantities:
            if max(collections.Counter(x.ingredient for x in ingredient_quantities).values()) > 1:
                raise ValueError("Passed multiple entries of the same ingredient in Meal init")

        if tags is not None:
            if isinstance(tags, MealTag):
                tags = (tags,)

            tags = set(tags)

            for x in tags:
                if not isinstance(x, MealTag):
                    raise ValueError(f"{x} is not a MealTag in Meal init")

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
        if not isinstance(key, MealMetadata):
            raise TypeError("'key' must be a MealMetadata instance")
        return self.metadata[key]


class MealCollection:
    def __init__(self, meals: Iterable[Meal] = None):
        if meals is None:
            self.meals = tuple()
        else:
            self.meals = tuple(x for x in meals)

        if not all(isinstance(x, Meal) for x in self.meals):
            raise TypeError("All entries in 'meals' must be Meals in MealCollection init")

    def copy(self) -> "MealCollection":
        return MealCollection(copy.copy(self.meals))

    def __repr__(self) -> str:
        return f"MealCollection({self.meals!r})"

    def __len__(self) -> int:
        return len(self.meals)

    def __bool__(self) -> bool:
        return len(self) > 0

    def __iter__(self) -> BasicIterator:
        return BasicIterator(self.meals)

    def __getitem__(self, index) -> Meal:
        return self.meals[index]

    def __add__(self, other: Union[Meal, "MealCollection"]) -> "MealCollection":
        if isinstance(other, Meal):
            return MealCollection(self.meals + (other,))

        if isinstance(other, MealCollection):
            return MealCollection(self.meals + other.meals)

        raise TypeError("'other' must be one of Meal or MealCollection")

    def __eq__(self, other: "MealCollection") -> bool:
        if not isinstance(other, MealCollection):
            return False

        if len(self) != len(other):
            return False

        for x in self:
            if x not in other:
                return False

        return True


class MealDiary:
    DATE_FORMAT = "%Y-%m-%d"

    def __init__(self, meal_diary: Optional[dict[dt.date, Meal]] = None):
        if meal_diary is not None:
            if not isinstance(meal_diary, dict):
                raise TypeError("meal_diary, if specified, must be a dictionary in MealDiary init")

        if meal_diary is None:
            self.meal_diary = dict()
        else:
            self.meal_diary = meal_diary.copy()

        if not all(isinstance(x, dt.date) for x in self.meal_diary):
            raise TypeError("All keys of 'meal_diary' must be datetime.dates in MealDiary init")

        if not all(isinstance(x, Meal) for x in self.meal_diary.values()):
            raise TypeError("All values of 'meal_diary' must be Meals in MealDiary init")

    def copy(self) -> "MealDiary":
        return MealDiary(copy.copy(self.meal_diary))

    def __getitem__(self, date: dt.date) -> Meal:
        if not isinstance(date, dt.date):
            raise TypeError("Key must be date in MealDiary.__getitem__")

        return self.meal_diary[date]

    def __setitem__(self, date: dt.date, meal: Meal) -> None:
        if not isinstance(date, dt.date):
            raise TypeError("Key must be date in MealDiary.__getitem__")
        if not isinstance(meal, Meal):
            raise TypeError("value must be a Meal in MealDiary.__getitem__")

        self.meal_diary[date] = meal

    @property
    def dates(self) -> Tuple[dt.date]:
        return tuple(self.meal_diary.keys())

    @property
    def meals(self) -> MealCollection:
        return MealCollection(self.meal_diary.values())

    def items(self):
        return self.meal_diary.items()

    def get_representation(self) -> dict[str, str]:
        """
        Represent the instance as a dictionary mapping date strings to
        meal names
        """

        ret = {date.strftime(MealDiary.DATE_FORMAT): meal.name for date, meal in self.items()}
        return dict(sorted(ret.items()))

    def __repr__(self) -> str:
        return str(self.get_representation())

    def __bool__(self) -> bool:
        return len(self.meal_diary) > 0

    def __eq__(self, other: "MealDiary") -> bool:
        if not isinstance(other, MealDiary):
            return False

        return self.meal_diary == other.meal_diary

    def __len__(self) -> int:
        return len(self.meal_diary)

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

        return MealDiary(
            {
                dt.datetime.strptime(date_string, MealDiary.DATE_FORMAT).date(): Meal.from_name(meal_name)
                for date_string, meal_name in dict_representation.items()
            }
        )

    def to_project_diary(self) -> None:
        self.to_file(PROJECT_DIARY_FILEPATH)

    @staticmethod
    def from_project_diary() -> "MealDiary":
        return MealDiary.from_file(PROJECT_DIARY_FILEPATH)

    def upsert(self, other: "MealDiary") -> "MealDiary":
        return MealDiary(self.meal_diary | other.meal_diary)

    def difference(self, other: "MealDiary") -> "MealDiary":
        return MealDiary({date: meal for date, meal in self.meal_diary.items() if date not in other.meal_diary.keys()})

    def filter_by_time_delta(self, date: dt.date, time_delta: dt.timedelta) -> "MealDiary":
        return MealDiary({meal_date: meal for meal_date, meal in self.items() if abs(meal_date - date) <= time_delta})

    def filter_dates(self, min_date: dt.date, max_date: Optional[dt.date] = None) -> "MealDiary":
        """
        Return a copy of the subset of the MealDiary with keys between
        the start_date (inclusive) and end_date (exclusive)

        If max_date is not specified, then return a copy of the subset
        of the MealDiary with keys and date >= the specified start_date
        """

        if not isinstance(min_date, dt.date):
            raise TypeError("min_date must be a datetime.date")

        if max_date is not None:
            if not isinstance(max_date, dt.date):
                raise TypeError("max_date must be a datetime.date")

        if max_date is None:
            return MealDiary({meal_date: meal for meal_date, meal in self.items() if meal_date >= min_date})

        return MealDiary(
            {meal_date: meal for meal_date, meal in self.items() if meal_date >= min_date if meal_date < max_date}
        )

    def except_dates(self, dates_to_exclude: Iterable[dt.date]) -> "MealDiary":
        """
        Return a copy of the MealDiary with the specified dates removed
        (if present)
        """

        if isinstance(dates_to_exclude, dt.date):
            dates_to_exclude = (dates_to_exclude,)

        dates_to_exclude = set(x for x in dates_to_exclude)

        if not all(isinstance(x, dt.date) for x in dates_to_exclude):
            raise TypeError("All passed dates must be datetime.dates")

        return MealDiary({meal_date: meal for meal_date, meal in self.items() if meal_date not in dates_to_exclude})

    def get_pretty_print_string(self) -> str:
        include_date_number_spacing = any(x.day >= 10 for x in self.dates)
        include_year = len(set(x.year for x in self.dates)) > 1

        lines = []
        for date in sorted(self.dates):
            meal = self[date]
            date_str = get_pretty_print_date_string(date, include_date_number_spacing, include_year)
            lines.append(f"{date_str}: {meal.name}")

        return "\n".join(lines)

    def filter_by_max_before_and_max_after_today(
        self,
        max_printed_previous_diary_entries: int,
        max_printed_next_diary_entries: int,
    ) -> "MealDiary":
        """
        Return a copy of this MealDiary, filtered to only dates which are close to
        today, specifically the 'max_printed_previous_diary_entries' closest before
        today, and the 'max_printed_next_diary_entries' closest after today
        """

        previous_dates = sorted([x for x in self.dates if x < dt.date.today()])
        if previous_dates:
            n_previous_dates_printed = min(len(previous_dates), max_printed_previous_diary_entries)
            if n_previous_dates_printed > 0:
                min_printed_date = previous_dates[-n_previous_dates_printed]
            else:
                min_printed_date = dt.date.today()
        else:
            min_printed_date = dt.date.today()

        next_dates = sorted([x for x in self.dates if x >= dt.date.today()])
        if next_dates:
            n_next_dates_printed = min(len(next_dates), max_printed_next_diary_entries)
            if n_next_dates_printed > 0:
                max_printed_date = next_dates[n_next_dates_printed - 1]
            else:
                max_printed_date = dt.date.today()
        else:
            max_printed_date = None

        return self.filter_dates(min_date=min_printed_date, max_date=max_printed_date)


class Meals(BaseEnum):
    BEEF_AND_ALE_STEW = Meal(
        name="Beef and Ale Stew",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.BAY_LEAVES, Unit.BOOL, True),
            IngredientQuantity(Ingredients.CARROT, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.CELERY, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.CHOPPED_TOMATOES, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.FLOUR, Unit.BOOL, True),
            IngredientQuantity(Ingredients.GUINNESS, Unit.MILLILITRE, 500),
            IngredientQuantity(Ingredients.ONION, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.POTATO, Unit.GRAM, 900),
            IngredientQuantity(Ingredients.STEWING_BEEF, Unit.GRAM, 750),
        ),
        properties={
            MealProperty.MEAT: MealMeat.BEEF,
        },
    )
    BURGERS = Meal(
        name="Burgers",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.BACON, Unit.BOOL, True),
            IngredientQuantity(Ingredients.BALSAMIC_VINEGAR, Unit.BOOL, True),
            IngredientQuantity(Ingredients.BEEF_MINCE, Unit.GRAM, 300),
            IngredientQuantity(Ingredients.BURGER_BUNS, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.DRIED_MUSTARD, Unit.BOOL, True),
            IngredientQuantity(Ingredients.EGGS, Unit.BOOL, True),
            IngredientQuantity(Ingredients.ITALIAN_HERBS, Unit.BOOL, True),
            IngredientQuantity(Ingredients.LETTUCE, Unit.BOOL, True),
            IngredientQuantity(Ingredients.MATURE_CHEDDAR_CHEESE, Unit.BOOL, True),
            IngredientQuantity(Ingredients.MAYONNAISE, Unit.BOOL, True),
            IngredientQuantity(Ingredients.SHALLOT, Unit.NUMBER, 1),
        ),
        properties={
            MealProperty.MEAT: MealMeat.BEEF,
        },
    )
    CHICKEN_AND_GREEN_BEAN_VERMICELLI_NOODLES = Meal(
        name="Chicken and Green Bean Vermicelli Noodles",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.BABY_CORN, Unit.GRAM, 150),
            IngredientQuantity(Ingredients.CARROT, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.CELERY, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.CHICKEN_BREAST, Unit.NUMBER, 3),
            IngredientQuantity(Ingredients.DARK_SOY_SAUCE, Unit.BOOL, True),
            IngredientQuantity(Ingredients.GARLIC_CLOVE, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.GINGER, Unit.BOOL, True),
            IngredientQuantity(Ingredients.GREEN_BEANS, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.ONION, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.PAK_CHOI, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.RED_PEPPER, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.SWEET_CHILLI_SAUCE, Unit.BOOL, True),
            IngredientQuantity(Ingredients.VERMICELLI_NOODLES, Unit.GRAM, 200),
        ),
        properties={
            MealProperty.MEAT: MealMeat.CHICKEN,
        },
    )
    CHICKEN_AND_LEEK_PIE = Meal(
        name="Chicken and Leek Pie",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.CHICKEN_BREAST, Unit.NUMBER, 4),
            IngredientQuantity(Ingredients.CHICKEN_STOCK, Unit.MILLILITRE, 150),
            IngredientQuantity(Ingredients.DOUBLE_CREAM, Unit.MILLILITRE, 150),
            IngredientQuantity(Ingredients.EGGS, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.FRESH_TARRAGON, Unit.BOOL, True),
            IngredientQuantity(Ingredients.GARLIC_CLOVE, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.LEEK, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.ONION, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.READY_ROLLED_PUFF_PASTRY, Unit.GRAM, 375),
            IngredientQuantity(Ingredients.VEGETABLE_OIL, Unit.BOOL, True),
            IngredientQuantity(Ingredients.WHITE_WINE, Unit.MILLILITRE, 150),
        ),
        properties={
            MealProperty.MEAT: MealMeat.CHICKEN,
        },
    )
    CHICKEN_FAJITAS = Meal(
        name="Chicken Fajitas",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.CHICKEN_BREAST, Unit.GRAM, 400),
            IngredientQuantity(Ingredients.CORIANDER, Unit.BOOL, True),
            IngredientQuantity(Ingredients.PAPRIKA, Unit.BOOL, True),
            IngredientQuantity(Ingredients.RED_ONION, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.RED_PEPPER, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.TORTILLA_WRAPS, Unit.BOOL, True),
            IngredientQuantity(Ingredients.YELLOW_PEPPER, Unit.NUMBER, 1),
        ),
        properties={
            MealProperty.MEAT: MealMeat.CHICKEN,
        },
    )
    CHICKEN_PICCATA = Meal(
        name="Chicken Piccata",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.CAPERS, Unit.JAR, 1),
            IngredientQuantity(Ingredients.CHICKEN_BREAST, Unit.NUMBER, 4),
            IngredientQuantity(Ingredients.CHICKEN_STOCK, Unit.MILLILITRE, 950),
            IngredientQuantity(Ingredients.FLOUR, Unit.BOOL, True),
            IngredientQuantity(Ingredients.LEMON_JUICE, Unit.MILLILITRE, 80),
            IngredientQuantity(Ingredients.OLIVE_OIL, Unit.BOOL, True),
            IngredientQuantity(Ingredients.RICE, Unit.GRAM, 250),
        ),
        properties={
            MealProperty.MEAT: MealMeat.CHICKEN,
        },
    )
    CHICKEN_SALTIMBOCCA = Meal(
        name="Chicken Saltimbocca",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.CHICKEN_BREAST, Unit.NUMBER, 3),
            IngredientQuantity(Ingredients.CHICKEN_BROTH, Unit.GRAM, 400),
            IngredientQuantity(Ingredients.LEMON, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.OLIVE_OIL, Unit.BOOL, True),
            IngredientQuantity(Ingredients.PARMESAN_CHEESE, Unit.GRAM, 20),
            IngredientQuantity(Ingredients.PROSCIUTTO, Unit.BOOL, True),
            IngredientQuantity(Ingredients.SPINACH, Unit.GRAM, 250),
        ),
        properties={
            MealProperty.MEAT: MealMeat.CHICKEN,
        },
    )
    CHICKEN_SOUP = Meal(
        name="Chicken Soup",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.BONELESS_SKINLESS_CHICKEN_THIGH, Unit.GRAM, 1400),
            IngredientQuantity(Ingredients.CELERY, Unit.NUMBER, 6),
            IngredientQuantity(Ingredients.MINI_CARROTS, Unit.BAG, 1),
            IngredientQuantity(Ingredients.MRS_JAMISONS_ORGANIC_CHICKEN_BASE, Unit.JAR, 1),
            IngredientQuantity(Ingredients.ONION, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.PARSLEY, Unit.BOOL, True),
        ),
        properties={
            MealProperty.MEAT: MealMeat.CHICKEN,
        },
    )
    CHICKEN_TALEGGIO = Meal(
        name="Chicken Taleggio",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.BALSAMIC_VINEGAR, Unit.BOOL, True),
            IngredientQuantity(Ingredients.BASIL, Unit.BOOL, True),
            IngredientQuantity(Ingredients.BREADCRUMBS, Unit.BOOL, True),
            IngredientQuantity(Ingredients.CHICKEN_BREAST, Unit.NUMBER, 6),
            IngredientQuantity(Ingredients.FULL_FAT_CREAM_CHEESE, Unit.BOOL, True),
            IngredientQuantity(Ingredients.GREEN_PESTO, Unit.BOOL, True),
            IngredientQuantity(Ingredients.OLIVE_OIL, Unit.BOOL, True),
            IngredientQuantity(Ingredients.PAPRIKA, Unit.BOOL, True),
            IngredientQuantity(Ingredients.TALEGGIO_CHEESE, Unit.GRAM, 175),
            IngredientQuantity(Ingredients.VINE_CHERRY_TOMATOES, Unit.GRAM, 400),
        ),
        properties={
            MealProperty.MEAT: MealMeat.CHICKEN,
        },
    )
    CHILLI_CHICKEN_THIGHS_WITH_CHERRY_TOMATOES = Meal(
        name="Chilli Chicken Thighs with Cherry Tomatoes",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.CHERRY_TOMATOES, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.CHICKEN_THIGH, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.GARLIC_CLOVE, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.OLIVE_OIL, Unit.BOOL, True),
            IngredientQuantity(Ingredients.RED_CHILLI, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.RICE, Unit.GRAM, 200),
        ),
        properties={
            MealProperty.MEAT: MealMeat.CHICKEN,
        },
    )
    CHILLI_CON_CARNE = Meal(
        name="Chilli con Carne",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.BEEF_MINCE, Unit.GRAM, 900),
            IngredientQuantity(Ingredients.CARROT, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.CELERY, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.CHOPPED_TOMATOES, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.FRESH_CHILLI, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.GARLIC_CLOVE, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.KIDNEY_BEANS, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.ONION, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.RICE, Unit.GRAM, 250),
            IngredientQuantity(Ingredients.TOMATO_PUREE, Unit.BOOL, True),
        ),
        properties={
            MealProperty.MEAT: MealMeat.BEEF,
        },
    )
    CURRY_LENTILS_IN_CROCK_POT = Meal(
        name="Curry Lentils in Crock Pot",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.BASMATI_RICE, Unit.GRAM, 400),
            IngredientQuantity(Ingredients.CAULIFLOWER_FLOURET, Unit.GRAM, 500),
            IngredientQuantity(Ingredients.CORIANDER, Unit.BOOL, True),
            IngredientQuantity(Ingredients.CUMIN, Unit.BOOL, True),
            IngredientQuantity(Ingredients.FROZEN_PEAS, Unit.GRAM, 200),
            IngredientQuantity(Ingredients.GARLIC_CLOVE, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.GINGER, Unit.BOOL, True),
            IngredientQuantity(Ingredients.JALAPENO, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.LENTILS, Unit.GRAM, 125),
            IngredientQuantity(Ingredients.LIGHT_COCONUT_MILK, Unit.MILLILITRE, 250),
            IngredientQuantity(Ingredients.LIME, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.SHALLOT, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.SHELLED_PISTACHIOS, Unit.GRAM, 100),
            IngredientQuantity(Ingredients.TOMATO_PASTE, Unit.BOOL, True),
            IngredientQuantity(Ingredients.VEGETABLE_BROTH, Unit.BOOL, True),
        ),
        properties={
            MealProperty.MEAT: MealMeat.NONE,
        },
    )
    FISH_PIE = Meal(
        name="Fish Pie",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.BABY_SPINACH, Unit.BOOL, True),
            IngredientQuantity(Ingredients.CARROT, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.CELERY, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.CHEDDAR_CHEESE, Unit.GRAM, 150),
            IngredientQuantity(Ingredients.LEMON, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.OLIVE_OIL, Unit.BOOL, True),
            IngredientQuantity(Ingredients.PARSLEY, Unit.BOOL, True),
            IngredientQuantity(Ingredients.POTATO, Unit.GRAM, 900),
            IngredientQuantity(Ingredients.RAW_KING_PRAWNS, Unit.GRAM, 125),
            IngredientQuantity(Ingredients.RED_CHILLI, Unit.NUMBER, 0.5),
            IngredientQuantity(Ingredients.SALMON_FILLET, Unit.GRAM, 300),
            IngredientQuantity(Ingredients.SMOKED_HADDOCK_FILLET, Unit.GRAM, 300),
        ),
        properties={
            MealProperty.MEAT: MealMeat.FISH,
        },
    )
    HONEY_GARLIC_SALMON = Meal(
        name="Honey-Garlic Salmon",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.BUTTER, Unit.BOOL, True),
            IngredientQuantity(Ingredients.FRESH_LEMON_JUICE, Unit.BOOL, True),
            IngredientQuantity(Ingredients.GARLIC_CLOVE, Unit.NUMBER, 4),
            IngredientQuantity(Ingredients.HONEY, Unit.BOOL, True),
            IngredientQuantity(Ingredients.PAPRIKA, Unit.BOOL, True),
            IngredientQuantity(Ingredients.SALMON_FILLET, Unit.GRAM, 1000),
            IngredientQuantity(Ingredients.SOY_SAUCE, Unit.BOOL, True),
        ),
        properties={
            MealProperty.MEAT: MealMeat.FISH,
        },
    )
    INDIAN_LAMB_WITH_SPICED_LENTILS = Meal(
        name="Indian Lamb with Spiced Lentils",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.BONELESS_LEG_OF_LAMB, Unit.GRAM, 500),
            IngredientQuantity(Ingredients.CARDAMOM, Unit.BOOL, True),
            IngredientQuantity(Ingredients.CINAMMON_STICK, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.CORIANDER, Unit.BOOL, True),
            IngredientQuantity(Ingredients.CUMIN, Unit.BOOL, True),
            IngredientQuantity(Ingredients.GARLIC_CLOVE, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.GINGER, Unit.BOOL, True),
            IngredientQuantity(Ingredients.LAMB_STOCK, Unit.MILLILITRE, 600),
            IngredientQuantity(Ingredients.LEMON, Unit.NUMBER, 0.5),
            IngredientQuantity(Ingredients.LENTILS, Unit.GRAM, 225),
            IngredientQuantity(Ingredients.ONION, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.PLUM_TOMATOES, Unit.NUMBER, 4),
            IngredientQuantity(Ingredients.RED_CHILLI, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.SUNFLOWER_OIL, Unit.BOOL, True),
            IngredientQuantity(Ingredients.TUMERIC, Unit.BOOL, True),
        ),
        properties={
            MealProperty.MEAT: MealMeat.LAMB,
        },
    )
    KEDGEREE = Meal(
        name="Kedgeree",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.CORIANDER, Unit.BOOL, True),
            IngredientQuantity(Ingredients.EGGS, Unit.NUMBER, 4),
            IngredientQuantity(Ingredients.GARLIC_CLOVE, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.GINGER, Unit.BOOL, True),
            IngredientQuantity(Ingredients.LONG_GRAIN_RICE, Unit.GRAM, 250),
            IngredientQuantity(Ingredients.MEDIUM_CURRY_POWDER, Unit.BOOL, True),
            IngredientQuantity(Ingredients.MILK, Unit.MILLILITRE, 150),
            IngredientQuantity(Ingredients.ONION, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.PARSLEY, Unit.BOOL, True),
            IngredientQuantity(Ingredients.SMOKED_HADDOCK_FILLET, Unit.GRAM, 400),
            IngredientQuantity(Ingredients.TUMERIC, Unit.BOOL, True),
            IngredientQuantity(Ingredients.VEGETABLE_STOCK, Unit.MILLILITRE, 350),
        ),
        properties={
            MealProperty.MEAT: MealMeat.FISH,
        },
    )
    LASAGNE = Meal(
        name="Lasagne",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.BEEF_MINCE, Unit.GRAM, 900),
            IngredientQuantity(Ingredients.BEEF_STOCK, Unit.BOOL, True),
            IngredientQuantity(Ingredients.BUTTER, Unit.BOOL, True),
            IngredientQuantity(Ingredients.CELERY, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.CHEDDAR_CHEESE, Unit.BOOL, True),
            IngredientQuantity(Ingredients.CHOPPED_TOMATOES, Unit.BOOL, True),
            IngredientQuantity(Ingredients.DIJON_MUSTARD, Unit.BOOL, True),
            IngredientQuantity(Ingredients.FLOUR, Unit.BOOL, True),
            IngredientQuantity(Ingredients.GARLIC_CLOVE, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.LASAGNE_SHEETS, Unit.BOOL, True),
            IngredientQuantity(Ingredients.MILK, Unit.BOOL, True),
            IngredientQuantity(Ingredients.ONION, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.PARMESAN_CHEESE, Unit.BOOL, True),
            IngredientQuantity(Ingredients.REDCURRANT_JELLY, Unit.BOOL, True),
            IngredientQuantity(Ingredients.THYME, Unit.BOOL, True),
            IngredientQuantity(Ingredients.TOMATO_PUREE, Unit.BOOL, True),
        ),
        properties={
            MealProperty.MEAT: MealMeat.BEEF,
        },
    )
    LEMON_LEEK_LINGUINE = Meal(
        name="Lemon Leek Linguine",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.LINGUINE, Unit.GRAM, 400),
            IngredientQuantity(Ingredients.LEEK, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.LEMON, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.GARLIC_CLOVE, Unit.BOOL, True),
            IngredientQuantity(Ingredients.CHICKEN_STOCK, Unit.BOOL, True),
            IngredientQuantity(Ingredients.BUTTER, Unit.BOOL, True),
            IngredientQuantity(Ingredients.PARMESAN_CHEESE, Unit.BOOL, True),
            IngredientQuantity(Ingredients.PARSLEY, Unit.BOOL, True),
            IngredientQuantity(Ingredients.CHIVES, Unit.BOOL, True),
        ),
        properties={
            MealProperty.MEAT: MealMeat.NONE,
        },
        tags=(MealTag.PASTA,),
    )
    MOUSSAKA = Meal(
        name="Moussaka",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.AUBERGINE, Unit.NUMBER, 4),
            IngredientQuantity(Ingredients.BUTTER, Unit.BOOL, True),
            IngredientQuantity(Ingredients.CINAMMON, Unit.BOOL, True),
            IngredientQuantity(Ingredients.EGGS, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.FLOUR, Unit.BOOL, True),
            IngredientQuantity(Ingredients.GARLIC_CLOVE, Unit.BOOL, True),
            IngredientQuantity(Ingredients.LAMB_MINCE, Unit.GRAM, 1000),
            IngredientQuantity(Ingredients.MILK, Unit.BOOL, True),
            IngredientQuantity(Ingredients.NUTMEG, Unit.BOOL, True),
            IngredientQuantity(Ingredients.ONION, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.PARMESAN_CHEESE, Unit.BOOL, True),
            IngredientQuantity(Ingredients.PARSLEY, Unit.BOOL, True),
            IngredientQuantity(Ingredients.RED_WINE, Unit.BOOL, True),
            IngredientQuantity(Ingredients.TOMATO_PUREE, Unit.BOOL, True),
        ),
        properties={
            MealProperty.MEAT: MealMeat.LAMB,
        },
    )
    PARMESAN_CRUST_BAKED_CHICKEN = Meal(
        name="Parmesan Crust Baked Chicken",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.CHICKEN_BREAST, Unit.GRAM, 500),
            IngredientQuantity(Ingredients.GARLIC_POWDER, Unit.BOOL, True),
            IngredientQuantity(Ingredients.ITALIAN_HERBS, Unit.BOOL, True),
            IngredientQuantity(Ingredients.MAYONNAISE, Unit.BOOL, True),
            IngredientQuantity(Ingredients.PARMESAN_CHEESE, Unit.BOOL, True),
        ),
        properties={
            MealProperty.MEAT: MealMeat.CHICKEN,
        },
    )
    PASTA_WITH_CHICKEN_AND_SUNDRIED_TOMATOES = Meal(
        name="Pasta with Chicken and Sundried Tomatoes",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.BABY_SPINACH, Unit.GRAM, 200),
            IngredientQuantity(Ingredients.CAYENNE_PEPPER, Unit.BOOL, True),
            IngredientQuantity(Ingredients.CHICKEN_BREAST, Unit.GRAM, 700),
            IngredientQuantity(Ingredients.CHICKEN_STOCK, Unit.MILLILITRE, 250),
            IngredientQuantity(Ingredients.CREAM, Unit.MILLILITRE, 250),
            IngredientQuantity(Ingredients.GARLIC_CLOVE, Unit.NUMBER, 3),
            IngredientQuantity(Ingredients.MOZARELLA_CHEESE, Unit.GRAM, 100),
            IngredientQuantity(Ingredients.PARMESAN_CHEESE, Unit.GRAM, 100),
            IngredientQuantity(Ingredients.PENNE_PASTA, Unit.GRAM, 300),
            IngredientQuantity(Ingredients.SUNDRIED_TOMATOES, Unit.GRAM, 750),
        ),
        properties={
            MealProperty.MEAT: MealMeat.CHICKEN,
        },
        tags=(MealTag.PASTA,),
    )
    PIZZA = Meal(
        name="Pizza",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.BASIL, Unit.BOOL, True),
            IngredientQuantity(Ingredients.CAPUTO_DOUBLE_ZERO_FLOUR, Unit.GRAM, 300),
            IngredientQuantity(Ingredients.FLOUR, Unit.GRAM, 300),
            IngredientQuantity(Ingredients.ACTIVE_DRY_YEAST, Unit.GRAM, 4),
            IngredientQuantity(Ingredients.HAM, Unit.BOOL, True),
            IngredientQuantity(Ingredients.HONEY, Unit.BOOL, True),
            IngredientQuantity(Ingredients.MOZARELLA_CHEESE, Unit.GRAM, 250),
            IngredientQuantity(Ingredients.OLIVE_OIL, Unit.BOOL, True),
            IngredientQuantity(Ingredients.PASSATA, Unit.MILLILITRE, 250),
            IngredientQuantity(Ingredients.PEPPERONI, Unit.BOOL, True),
        ),
        properties={
            MealProperty.MEAT: MealMeat.PORK,
        },
    )
    QUICHE_LORRAINE = Meal(
        name="Quiche Lorraine",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.BACON, Unit.NUMBER, 8),
            IngredientQuantity(Ingredients.CHERRY_TOMATOES, Unit.BOOL, True),
            IngredientQuantity(Ingredients.DOUBLE_CREAM, Unit.MILLILITRE, 275),
            IngredientQuantity(Ingredients.EGGS, Unit.NUMBER, 3),
            IngredientQuantity(Ingredients.GRUYERE_CHEESE, Unit.GRAM, 75),
            IngredientQuantity(Ingredients.SHORTCRUST_PASTRY, Unit.BOOL, True),
        ),
        properties={
            MealProperty.MEAT: MealMeat.PORK,
        },
    )
    ROAST_BEEF = Meal(
        name="Roast Beef",
        ingredient_quantities=(IngredientQuantity(Ingredients.BEEF_JOINT, Unit.BOOL, True),),
        properties={
            MealProperty.MEAT: MealMeat.BEEF,
        },
        tags=(MealTag.ROAST,),
    )
    ROAST_CHICKEN = Meal(
        name="Roast Chicken",
        ingredient_quantities=(IngredientQuantity(Ingredients.WHOLE_CHICKEN, Unit.BOOL, True),),
        properties={
            MealProperty.MEAT: MealMeat.CHICKEN,
        },
        tags=(MealTag.ROAST,),
    )
    ROAST_LAMB = Meal(
        name="Roast Lamb",
        ingredient_quantities=(IngredientQuantity(Ingredients.LEG_OF_LAMB, Unit.BOOL, True),),
        properties={
            MealProperty.MEAT: MealMeat.LAMB,
        },
        tags=(MealTag.ROAST,),
    )
    ROAST_PORK = Meal(
        name="Roast Pork",
        ingredient_quantities=(IngredientQuantity(Ingredients.PORK_JOINT, Unit.BOOL, True),),
        properties={
            MealProperty.MEAT: MealMeat.PORK,
        },
        tags=(MealTag.ROAST,),
    )
    SAAG_PANEER = Meal(
        name="Saag Paneer",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.CAYENNE_PEPPER, Unit.BOOL, True),
            IngredientQuantity(Ingredients.COCONUT_MILK, Unit.MILLILITRE, 350),
            IngredientQuantity(Ingredients.CUMIN, Unit.BOOL, True),
            IngredientQuantity(Ingredients.DRIED_FENUGREEK, Unit.BOOL, True),
            IngredientQuantity(Ingredients.GARAM_MASALA, Unit.BOOL, True),
            IngredientQuantity(Ingredients.GARLIC_CLOVE, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.GHEE, Unit.BOOL, True),
            IngredientQuantity(Ingredients.GINGER, Unit.BOOL, True),
            IngredientQuantity(Ingredients.KOSHER_SALT, Unit.BOOL, True),
            IngredientQuantity(Ingredients.ONION, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.PANEER_CHEESE, Unit.GRAM, 350),
            IngredientQuantity(Ingredients.SPINACH, Unit.GRAM, 450),
            IngredientQuantity(Ingredients.TUMERIC, Unit.BOOL, True),
        ),
        properties={
            MealProperty.MEAT: MealMeat.NONE,
        },
        tags=(MealTag.INDIAN,),
    )
    SHEPHERDS_PIE = Meal(
        name="Shepherds Pie",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.BEEF_MINCE, Unit.GRAM, 500),
            IngredientQuantity(Ingredients.BEEF_STOCK, Unit.BOOL, True),
            IngredientQuantity(Ingredients.BUTTER, Unit.BOOL, True),
            IngredientQuantity(Ingredients.CARROT, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.CHOPPED_TOMATOES, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.FLOUR, Unit.BOOL, True),
            IngredientQuantity(Ingredients.LAMB_MINCE, Unit.GRAM, 500),
            IngredientQuantity(Ingredients.OLIVE_OIL, Unit.BOOL, True),
            IngredientQuantity(Ingredients.ONION, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.POTATO, Unit.GRAM, 1000),
            IngredientQuantity(Ingredients.RED_WINE, Unit.MILLILITRE, 200),
            IngredientQuantity(Ingredients.THYME, Unit.BOOL, True),
            IngredientQuantity(Ingredients.WORCESTERSHIRE_SAUCE, Unit.BOOL, True),
        ),
        properties={
            MealProperty.MEAT: MealMeat.BEEF,
        },
        tags=(MealTag.PASTA,),
    )
    SLOW_COOKER_BEEF_BOURGUIGNON = Meal(
        name="Slow Cooker Beef Bourgignon",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.BAY_LEAVES, Unit.BOOL, True),
            IngredientQuantity(Ingredients.BEEF_BROTH, Unit.MILLILITRE, 500),
            IngredientQuantity(Ingredients.BEEF_CHUCK_STEAK, Unit.GRAM, 900),
            IngredientQuantity(Ingredients.BUTTER, Unit.BOOL, True),
            IngredientQuantity(Ingredients.CARROT, Unit.NUMBER, 4),
            IngredientQuantity(Ingredients.CIPOLLINI_ONION, Unit.GRAM, 450),
            IngredientQuantity(Ingredients.DRY_RED_WINE, Unit.MILLILITRE, 700),
            IngredientQuantity(Ingredients.FLOUR, Unit.BOOL, True),
            IngredientQuantity(Ingredients.GARLIC_CLOVE, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.KOSHER_SALT, Unit.BOOL, True),
            IngredientQuantity(Ingredients.PARSLEY, Unit.BOOL, True),
            IngredientQuantity(Ingredients.THICK_CUT_BACON, Unit.GRAM, 300),
            IngredientQuantity(Ingredients.THYME, Unit.BOOL, True),
            IngredientQuantity(Ingredients.TOMATO_PUREE, Unit.GRAM, 50),
        ),
        properties={
            MealProperty.MEAT: MealMeat.BEEF,
        },
    )
    SLOW_COOKER_CHICKEN_TIKKA_MASALA = Meal(
        name="Slow Cooker Chicken Tikka Masala",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.CAYENNE_PEPPER, Unit.BOOL, True),
            IngredientQuantity(Ingredients.CHICKEN_BREAST, Unit.NUMBER, 4),
            IngredientQuantity(Ingredients.CORIANDER, Unit.BOOL, True),
            IngredientQuantity(Ingredients.CUMIN, Unit.BOOL, True),
            IngredientQuantity(Ingredients.DOUBLE_CREAM, Unit.MILLILITRE, 250),
            IngredientQuantity(Ingredients.GARAM_MASALA, Unit.BOOL, True),
            IngredientQuantity(Ingredients.GARLIC_CLOVE, Unit.NUMBER, 5),
            IngredientQuantity(Ingredients.ONION, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.RICE, Unit.GRAM, 500),
            IngredientQuantity(Ingredients.TOMATO_PUREE, Unit.BOOL, True),
            IngredientQuantity(Ingredients.YOGURT, Unit.MILLILITRE, 250),
        ),
        properties={
            MealProperty.MEAT: MealMeat.CHICKEN,
        },
        tags=(MealTag.INDIAN,),
    )
    SLOW_COOKER_HONEY_GARLIC_CHICKEN_AND_VEGGIES = Meal(
        name="Slow Cooker Honey Garlic Chicken and Veggies",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.BABY_CARROT, Unit.GRAM, 450),
            IngredientQuantity(Ingredients.BABY_RED_POTATO, Unit.GRAM, 450),
            IngredientQuantity(Ingredients.CHICKEN_THIGH, Unit.NUMBER, 8),
            IngredientQuantity(Ingredients.DRIED_BASIL, Unit.BOOL, True),
            IngredientQuantity(Ingredients.DRIED_OREGANO, Unit.BOOL, True),
            IngredientQuantity(Ingredients.GARLIC_CLOVE, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.GREEN_BEANS, Unit.GRAM, 450),
            IngredientQuantity(Ingredients.HONEY, Unit.MILLILITRE, 100),
            IngredientQuantity(Ingredients.KETCHUP, Unit.MILLILITRE, 50),
            IngredientQuantity(Ingredients.PARSLEY, Unit.BOOL, True),
            IngredientQuantity(Ingredients.RED_PEPPER_FLAKES, Unit.BOOL, True),
            IngredientQuantity(Ingredients.SOY_SAUCE, Unit.MILLILITRE, 100),
        ),
        properties={
            MealProperty.MEAT: MealMeat.CHICKEN,
        },
    )
    SPAGHETTI_BOLOGNESE = Meal(
        name="Spaghetti Bolognese",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.BAY_LEAVES, Unit.BOOL, True),
            IngredientQuantity(Ingredients.BEEF_MINCE, Unit.GRAM, 500),
            IngredientQuantity(Ingredients.CARROT, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.CELERY, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.CHOPPED_TOMATOES, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.GARLIC_CLOVE, Unit.NUMBER, 3),
            IngredientQuantity(Ingredients.MIXED_HERBS, Unit.BOOL, True),
            IngredientQuantity(Ingredients.ONION, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.OREGANO, Unit.BOOL, True),
            IngredientQuantity(Ingredients.PARMESAN_CHEESE, Unit.BOOL, True),
            IngredientQuantity(Ingredients.PORK_MINCE, Unit.GRAM, 500),
            IngredientQuantity(Ingredients.SPAGHETTI, Unit.BOOL, True),
            IngredientQuantity(Ingredients.TOMATO_PUREE, Unit.BOOL, True),
        ),
        properties={
            MealProperty.MEAT: MealMeat.BEEF,
        },
        tags=(MealTag.PASTA,),
    )
    STICKY_CHINESE_PORK_BELLY = Meal(
        name="Sticky Chinese Pork Belly",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.BROWN_SUGAR, Unit.BOOL, True),
            IngredientQuantity(Ingredients.CASTER_SUGAR, Unit.BOOL, True),
            IngredientQuantity(Ingredients.CHICKEN_STOCK, Unit.MILLILITRE, 1000),
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
            MealProperty.MEAT: MealMeat.PORK,
        },
    )
    TURKEY_SWEET_POTATO_SHEPHERDS_PIE = Meal(
        name="Turkey Sweet Potato Shepherds Pie",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.CARROT, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.CELERY, Unit.NUMBER, 3),
            IngredientQuantity(Ingredients.COCONUT_MILK, Unit.MILLILITRE, 150),
            IngredientQuantity(Ingredients.COCONUT_OIL, Unit.BOOL, True),
            IngredientQuantity(Ingredients.DRIED_THYME, Unit.BOOL, True),
            IngredientQuantity(Ingredients.GARLIC_POWDER, Unit.BOOL, True),
            IngredientQuantity(Ingredients.ONION, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.OREGANO, Unit.BOOL, True),
            IngredientQuantity(Ingredients.SWEET_POTATO, Unit.NUMBER, 3),
            IngredientQuantity(Ingredients.TURKEY_MINCE, Unit.GRAM, 500),
        ),
        properties={
            MealProperty.MEAT: MealMeat.TURKEY,
        },
    )
    TURKEY_STUFFED_PEPPERS = Meal(
        name="Turkey Stuffed Peppers",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.EGGS, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.GREEN_PEPPER, Unit.NUMBER, 4),
            IngredientQuantity(Ingredients.ONION, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.PASSATA, Unit.MILLILITRE, 500),
            IngredientQuantity(Ingredients.RICE, Unit.GRAM, 400),
            IngredientQuantity(Ingredients.TOMATO_SOUP, Unit.JAR, 1),
            IngredientQuantity(Ingredients.TURKEY_MINCE, Unit.GRAM, 500),
        ),
        properties={
            MealProperty.MEAT: MealMeat.TURKEY,
        },
    )


meal_names_to_meal_map = {x.value.name.upper(): x.value for x in Meals}
