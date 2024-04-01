from __future__ import annotations

import collections
import copy
import datetime as dt
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Optional, Tuple, Union

from mealprep.basic_iterator import BasicIterator
from mealprep.constants import BaseEnum, MealMeat, MealMetadata, MealProperty, MealTag, Unit
from mealprep.ingredient import Ingredient, IngredientQuantity, IngredientQuantityCollection
from mealprep.loc import DATA_DIR
from mealprep.utils import get_pretty_print_date_string


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
                dt.datetime.strptime(date_string, MealDiary.DATE_FORMAT).date(): Meal.from_name(
                    meal_name
                )
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
        return MealDiary(
            {
                date: meal
                for date, meal in self.meal_diary.items()
                if date not in other.meal_diary.keys()
            }
        )

    def filter_by_time_delta(self, date: dt.date, time_delta: dt.timedelta) -> "MealDiary":
        return MealDiary(
            {
                meal_date: meal
                for meal_date, meal in self.items()
                if abs(meal_date - date) <= time_delta
            }
        )

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
            return MealDiary(
                {meal_date: meal for meal_date, meal in self.items() if meal_date >= min_date}
            )

        return MealDiary(
            {
                meal_date: meal
                for meal_date, meal in self.items()
                if meal_date >= min_date
                if meal_date < max_date
            }
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

        return MealDiary(
            {
                meal_date: meal
                for meal_date, meal in self.items()
                if meal_date not in dates_to_exclude
            }
        )

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
        ingredient_quantities=IngredientQuantityCollection(
            (
                IngredientQuantity(Ingredient.from_name("Bay Leaves"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Carrot"), Unit.NUMBER, 2),
                IngredientQuantity(Ingredient.from_name("Celery"), Unit.NUMBER, 2),
                IngredientQuantity(Ingredient.from_name("Chopped Tomatoes"), Unit.NUMBER, 1),
                IngredientQuantity(Ingredient.from_name("Flour"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Guinness"), Unit.MILLILITRE, 500),
                IngredientQuantity(Ingredient.from_name("Onion"), Unit.NUMBER, 2),
                IngredientQuantity(Ingredient.from_name("Potato"), Unit.GRAM, 900),
                IngredientQuantity(Ingredient.from_name("Stewing Beef"), Unit.GRAM, 750),
            )
        ),
        properties={
            MealProperty.MEAT: MealMeat.BEEF,
        },
    )
    BURGERS = Meal(
        name="Burgers",
        ingredient_quantities=IngredientQuantityCollection(
            (
                IngredientQuantity(Ingredient.from_name("Bacon"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Balsamic Vinegar"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Beef Mince"), Unit.GRAM, 300),
                IngredientQuantity(Ingredient.from_name("Burger Buns"), Unit.NUMBER, 1),
                IngredientQuantity(Ingredient.from_name("Dried Mustard"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Eggs"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Italian Herbs"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Lettuce"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Mature Cheddar Cheese"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Mayonnaise"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Shallot"), Unit.NUMBER, 1),
            )
        ),
        properties={
            MealProperty.MEAT: MealMeat.BEEF,
        },
    )
    CHICKEN_AND_GREEN_BEAN_VERMICELLI_NOODLES = Meal(
        name="Chicken and Green Bean Vermicelli Noodles",
        ingredient_quantities=IngredientQuantityCollection(
            (
                IngredientQuantity(Ingredient.from_name("Baby Corn"), Unit.GRAM, 150),
                IngredientQuantity(Ingredient.from_name("Carrot"), Unit.NUMBER, 2),
                IngredientQuantity(Ingredient.from_name("Celery"), Unit.NUMBER, 1),
                IngredientQuantity(Ingredient.from_name("Chicken Breast"), Unit.NUMBER, 3),
                IngredientQuantity(Ingredient.from_name("Dark Soy Sauce"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Garlic Clove"), Unit.NUMBER, 2),
                IngredientQuantity(Ingredient.from_name("Ginger"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Green Beans"), Unit.NUMBER, 1),
                IngredientQuantity(Ingredient.from_name("Onion"), Unit.NUMBER, 1),
                IngredientQuantity(Ingredient.from_name("Pak Choi"), Unit.NUMBER, 1),
                IngredientQuantity(Ingredient.from_name("Red Pepper"), Unit.NUMBER, 1),
                IngredientQuantity(Ingredient.from_name("Sweet Chilli Sauce"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Vermicelli Noodles"), Unit.GRAM, 200),
            )
        ),
        properties={
            MealProperty.MEAT: MealMeat.CHICKEN,
        },
    )
    CHICKEN_AND_LEEK_PIE = Meal(
        name="Chicken and Leek Pie",
        ingredient_quantities=IngredientQuantityCollection(
            (
                IngredientQuantity(Ingredient.from_name("Chicken Breast"), Unit.NUMBER, 4),
                IngredientQuantity(Ingredient.from_name("Chicken Stock"), Unit.MILLILITRE, 150),
                IngredientQuantity(Ingredient.from_name("Double Cream"), Unit.MILLILITRE, 150),
                IngredientQuantity(Ingredient.from_name("Eggs"), Unit.NUMBER, 1),
                IngredientQuantity(Ingredient.from_name("Fresh Tarragon"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Garlic Clove"), Unit.NUMBER, 1),
                IngredientQuantity(Ingredient.from_name("Leek"), Unit.NUMBER, 2),
                IngredientQuantity(Ingredient.from_name("Onion"), Unit.NUMBER, 1),
                IngredientQuantity(
                    Ingredient.from_name("Ready Rolled Puff Pastry"), Unit.GRAM, 375
                ),
                IngredientQuantity(Ingredient.from_name("Vegetable Oil"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("White Wine"), Unit.MILLILITRE, 150),
            )
        ),
        properties={
            MealProperty.MEAT: MealMeat.CHICKEN,
        },
    )
    CHICKEN_FAJITAS = Meal(
        name="Chicken Fajitas",
        ingredient_quantities=IngredientQuantityCollection(
            (
                IngredientQuantity(Ingredient.from_name("Chicken Breast"), Unit.GRAM, 400),
                IngredientQuantity(Ingredient.from_name("Coriander"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Paprika"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Red Onion"), Unit.NUMBER, 2),
                IngredientQuantity(Ingredient.from_name("Red Pepper"), Unit.NUMBER, 1),
                IngredientQuantity(Ingredient.from_name("Tortilla Wraps"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Yellow Pepper"), Unit.NUMBER, 1),
            )
        ),
        properties={
            MealProperty.MEAT: MealMeat.CHICKEN,
        },
    )
    CHICKEN_PICCATA = Meal(
        name="Chicken Piccata",
        ingredient_quantities=IngredientQuantityCollection(
            (
                IngredientQuantity(Ingredient.from_name("Capers"), Unit.JAR, 1),
                IngredientQuantity(Ingredient.from_name("Chicken Breast"), Unit.NUMBER, 4),
                IngredientQuantity(Ingredient.from_name("Chicken Stock"), Unit.MILLILITRE, 950),
                IngredientQuantity(Ingredient.from_name("Flour"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Lemon Juice"), Unit.MILLILITRE, 80),
                IngredientQuantity(Ingredient.from_name("Olive Oil"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Rice"), Unit.GRAM, 250),
            )
        ),
        properties={
            MealProperty.MEAT: MealMeat.CHICKEN,
        },
    )
    CHICKEN_SALTIMBOCCA = Meal(
        name="Chicken Saltimbocca",
        ingredient_quantities=IngredientQuantityCollection(
            (
                IngredientQuantity(Ingredient.from_name("Chicken Breast"), Unit.NUMBER, 3),
                IngredientQuantity(Ingredient.from_name("Chicken Broth"), Unit.GRAM, 400),
                IngredientQuantity(Ingredient.from_name("Lemon"), Unit.NUMBER, 1),
                IngredientQuantity(Ingredient.from_name("Olive Oil"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Parmesan Cheese"), Unit.GRAM, 20),
                IngredientQuantity(Ingredient.from_name("Prosciutto"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Spinach"), Unit.GRAM, 250),
            )
        ),
        properties={
            MealProperty.MEAT: MealMeat.CHICKEN,
        },
    )
    CHICKEN_SOUP = Meal(
        name="Chicken Soup",
        ingredient_quantities=IngredientQuantityCollection(
            (
                IngredientQuantity(
                    Ingredient.from_name("Boneless Skinless Chicken Thigh"), Unit.GRAM, 1400
                ),
                IngredientQuantity(Ingredient.from_name("Celery"), Unit.NUMBER, 6),
                IngredientQuantity(Ingredient.from_name("Mini Carrots"), Unit.BAG, 1),
                IngredientQuantity(
                    Ingredient.from_name("Mrs Jamison's Organic Chicken Base"), Unit.JAR, 1
                ),
                IngredientQuantity(Ingredient.from_name("Onion"), Unit.NUMBER, 2),
                IngredientQuantity(Ingredient.from_name("Parsley"), Unit.BOOL, True),
            )
        ),
        properties={
            MealProperty.MEAT: MealMeat.CHICKEN,
        },
    )
    CHICKEN_TALEGGIO = Meal(
        name="Chicken Taleggio",
        ingredient_quantities=IngredientQuantityCollection(
            (
                IngredientQuantity(Ingredient.from_name("Balsamic Vinegar"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Basil"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Breadcrumbs"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Chicken Breast"), Unit.NUMBER, 6),
                IngredientQuantity(Ingredient.from_name("Full Fat Cream Cheese"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Green Pesto"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Olive Oil"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Paprika"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Taleggio Cheese"), Unit.GRAM, 175),
                IngredientQuantity(Ingredient.from_name("Vine Cherry Tomatoes"), Unit.GRAM, 400),
            )
        ),
        properties={
            MealProperty.MEAT: MealMeat.CHICKEN,
        },
    )
    CHILLI_CHICKEN_THIGHS_WITH_CHERRY_TOMATOES = Meal(
        name="Chilli Chicken Thighs with Cherry Tomatoes",
        ingredient_quantities=IngredientQuantityCollection(
            (
                IngredientQuantity(Ingredient.from_name("Cherry Tomatoes"), Unit.NUMBER, 2),
                IngredientQuantity(Ingredient.from_name("Chicken Thigh"), Unit.NUMBER, 2),
                IngredientQuantity(Ingredient.from_name("Garlic Clove"), Unit.NUMBER, 2),
                IngredientQuantity(Ingredient.from_name("Olive Oil"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Red Chilli"), Unit.NUMBER, 2),
                IngredientQuantity(Ingredient.from_name("Rice"), Unit.GRAM, 200),
            )
        ),
        properties={
            MealProperty.MEAT: MealMeat.CHICKEN,
        },
    )
    CHILLI_CON_CARNE = Meal(
        name="Chilli con Carne",
        ingredient_quantities=IngredientQuantityCollection(
            (
                IngredientQuantity(Ingredient.from_name("Beef Mince"), Unit.GRAM, 900),
                IngredientQuantity(Ingredient.from_name("Carrot"), Unit.NUMBER, 1),
                IngredientQuantity(Ingredient.from_name("Celery"), Unit.NUMBER, 1),
                IngredientQuantity(Ingredient.from_name("Chopped Tomatoes"), Unit.NUMBER, 1),
                IngredientQuantity(Ingredient.from_name("Fresh Chilli"), Unit.NUMBER, 1),
                IngredientQuantity(Ingredient.from_name("Garlic Clove"), Unit.NUMBER, 2),
                IngredientQuantity(Ingredient.from_name("Kidney Beans"), Unit.NUMBER, 1),
                IngredientQuantity(Ingredient.from_name("Onion"), Unit.NUMBER, 1),
                IngredientQuantity(Ingredient.from_name("Rice"), Unit.GRAM, 250),
                IngredientQuantity(Ingredient.from_name("Tomato Puree"), Unit.BOOL, True),
            )
        ),
        properties={
            MealProperty.MEAT: MealMeat.BEEF,
        },
    )
    CURRY_LENTILS_IN_CROCK_POT = Meal(
        name="Curry Lentils in Crock Pot",
        ingredient_quantities=IngredientQuantityCollection(
            (
                IngredientQuantity(Ingredient.from_name("Basmati Rice"), Unit.GRAM, 400),
                IngredientQuantity(Ingredient.from_name("Cauliflower Flouret"), Unit.GRAM, 500),
                IngredientQuantity(Ingredient.from_name("Coriander"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Cumin"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Frozen Peas"), Unit.GRAM, 200),
                IngredientQuantity(Ingredient.from_name("Garlic Clove"), Unit.NUMBER, 2),
                IngredientQuantity(Ingredient.from_name("Ginger"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Jalapeno"), Unit.NUMBER, 1),
                IngredientQuantity(Ingredient.from_name("Lentils"), Unit.GRAM, 125),
                IngredientQuantity(
                    Ingredient.from_name("Light Coconut Milk"), Unit.MILLILITRE, 250
                ),
                IngredientQuantity(Ingredient.from_name("Lime"), Unit.NUMBER, 1),
                IngredientQuantity(Ingredient.from_name("Shallot"), Unit.NUMBER, 2),
                IngredientQuantity(Ingredient.from_name("Shelled Pistachios"), Unit.GRAM, 100),
                IngredientQuantity(Ingredient.from_name("Tomato Paste"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Vegetable Broth"), Unit.BOOL, True),
            )
        ),
        properties={
            MealProperty.MEAT: MealMeat.NONE,
        },
    )
    FISH_PIE = Meal(
        name="Fish Pie",
        ingredient_quantities=IngredientQuantityCollection(
            (
                IngredientQuantity(Ingredient.from_name("Baby Spinach"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Carrot"), Unit.NUMBER, 1),
                IngredientQuantity(Ingredient.from_name("Celery"), Unit.NUMBER, 2),
                IngredientQuantity(Ingredient.from_name("Cheddar Cheese"), Unit.GRAM, 150),
                IngredientQuantity(Ingredient.from_name("Lemon"), Unit.NUMBER, 1),
                IngredientQuantity(Ingredient.from_name("Olive Oil"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Parsley"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Potato"), Unit.GRAM, 900),
                IngredientQuantity(Ingredient.from_name("Raw King Prawns"), Unit.GRAM, 125),
                IngredientQuantity(Ingredient.from_name("Red Chilli"), Unit.NUMBER, 0.5),
                IngredientQuantity(Ingredient.from_name("Salmon Fillet"), Unit.GRAM, 300),
                IngredientQuantity(Ingredient.from_name("Smoked Haddock Fillet"), Unit.GRAM, 300),
            )
        ),
        properties={
            MealProperty.MEAT: MealMeat.FISH,
        },
    )
    HONEY_GARLIC_SALMON = Meal(
        name="Honey-Garlic Salmon",
        ingredient_quantities=IngredientQuantityCollection(
            (
                IngredientQuantity(Ingredient.from_name("Butter"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Fresh Lemon Juice"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Garlic Clove"), Unit.NUMBER, 4),
                IngredientQuantity(Ingredient.from_name("Honey"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Paprika"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Salmon Fillet"), Unit.GRAM, 1000),
                IngredientQuantity(Ingredient.from_name("Soy Sauce"), Unit.BOOL, True),
            )
        ),
        properties={
            MealProperty.MEAT: MealMeat.FISH,
        },
    )
    INDIAN_LAMB_WITH_SPICED_LENTILS = Meal(
        name="Indian Lamb with Spiced Lentils",
        ingredient_quantities=IngredientQuantityCollection(
            (
                IngredientQuantity(Ingredient.from_name("Boneless Leg of Lamb"), Unit.GRAM, 500),
                IngredientQuantity(Ingredient.from_name("Cardamom"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Cinammon Stick"), Unit.NUMBER, 1),
                IngredientQuantity(Ingredient.from_name("Coriander"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Cumin"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Garlic Clove"), Unit.NUMBER, 2),
                IngredientQuantity(Ingredient.from_name("Ginger"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Lamb Stock"), Unit.MILLILITRE, 600),
                IngredientQuantity(Ingredient.from_name("Lemon"), Unit.NUMBER, 0.5),
                IngredientQuantity(Ingredient.from_name("Lentils"), Unit.GRAM, 225),
                IngredientQuantity(Ingredient.from_name("Onion"), Unit.NUMBER, 1),
                IngredientQuantity(Ingredient.from_name("Plum Tomatoes"), Unit.NUMBER, 4),
                IngredientQuantity(Ingredient.from_name("Red Chilli"), Unit.NUMBER, 1),
                IngredientQuantity(Ingredient.from_name("Sunflower Oil"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Tumeric"), Unit.BOOL, True),
            )
        ),
        properties={
            MealProperty.MEAT: MealMeat.LAMB,
        },
    )
    KEDGEREE = Meal(
        name="Kedgeree",
        ingredient_quantities=IngredientQuantityCollection(
            (
                IngredientQuantity(Ingredient.from_name("Coriander"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Eggs"), Unit.NUMBER, 4),
                IngredientQuantity(Ingredient.from_name("Garlic Clove"), Unit.NUMBER, 1),
                IngredientQuantity(Ingredient.from_name("Ginger"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Long-Grain Rice"), Unit.GRAM, 250),
                IngredientQuantity(Ingredient.from_name("Medium Curry Powder"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Milk"), Unit.MILLILITRE, 150),
                IngredientQuantity(Ingredient.from_name("Onion"), Unit.NUMBER, 1),
                IngredientQuantity(Ingredient.from_name("Parsley"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Smoked Haddock Fillet"), Unit.GRAM, 400),
                IngredientQuantity(Ingredient.from_name("Tumeric"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Vegetable Stock"), Unit.MILLILITRE, 350),
            )
        ),
        properties={
            MealProperty.MEAT: MealMeat.FISH,
        },
    )
    LASAGNE = Meal(
        name="Lasagne",
        ingredient_quantities=IngredientQuantityCollection(
            (
                IngredientQuantity(Ingredient.from_name("Beef Mince"), Unit.GRAM, 900),
                IngredientQuantity(Ingredient.from_name("Beef Stock"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Butter"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Celery"), Unit.NUMBER, 2),
                IngredientQuantity(Ingredient.from_name("Cheddar Cheese"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Chopped Tomatoes"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Dijon Mustard"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Flour"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Garlic Clove"), Unit.NUMBER, 2),
                IngredientQuantity(Ingredient.from_name("Lasagne Sheets"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Milk"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Onion"), Unit.NUMBER, 2),
                IngredientQuantity(Ingredient.from_name("Parmesan Cheese"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Redcurrant Jelly"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Thyme"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Tomato Puree"), Unit.BOOL, True),
            )
        ),
        properties={
            MealProperty.MEAT: MealMeat.BEEF,
        },
    )
    LEMON_LEEK_LINGUINE = Meal(
        name="Lemon Leek Linguine",
        ingredient_quantities=IngredientQuantityCollection(
            (
                IngredientQuantity(Ingredient.from_name("Linguine"), Unit.GRAM, 400),
                IngredientQuantity(Ingredient.from_name("Leek"), Unit.NUMBER, 2),
                IngredientQuantity(Ingredient.from_name("Lemon"), Unit.NUMBER, 2),
                IngredientQuantity(Ingredient.from_name("Garlic Clove"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Chicken Stock"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Butter"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Parmesan Cheese"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Parsley"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Chives"), Unit.BOOL, True),
            )
        ),
        properties={
            MealProperty.MEAT: MealMeat.NONE,
        },
        tags=(MealTag.PASTA,),
    )
    MOUSSAKA = Meal(
        name="Moussaka",
        ingredient_quantities=IngredientQuantityCollection(
            (
                IngredientQuantity(Ingredient.from_name("Aubergine"), Unit.NUMBER, 4),
                IngredientQuantity(Ingredient.from_name("Butter"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Cinammon"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Eggs"), Unit.NUMBER, 2),
                IngredientQuantity(Ingredient.from_name("Flour"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Garlic Clove"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Lamb Mince"), Unit.GRAM, 1000),
                IngredientQuantity(Ingredient.from_name("Milk"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Nutmeg"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Onion"), Unit.NUMBER, 2),
                IngredientQuantity(Ingredient.from_name("Parmesan Cheese"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Parsley"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Red Wine"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Tomato Puree"), Unit.BOOL, True),
            )
        ),
        properties={
            MealProperty.MEAT: MealMeat.LAMB,
        },
    )
    PARMESAN_CRUST_BAKED_CHICKEN = Meal(
        name="Parmesan Crust Baked Chicken",
        ingredient_quantities=IngredientQuantityCollection(
            (
                IngredientQuantity(Ingredient.from_name("Chicken Breast"), Unit.GRAM, 500),
                IngredientQuantity(Ingredient.from_name("Garlic Powder"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Italian Herbs"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Mayonnaise"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Parmesan Cheese"), Unit.BOOL, True),
            )
        ),
        properties={
            MealProperty.MEAT: MealMeat.CHICKEN,
        },
    )
    PASTA_WITH_CHICKEN_AND_SUNDRIED_TOMATOES = Meal(
        name="Pasta with Chicken and Sundried Tomatoes",
        ingredient_quantities=IngredientQuantityCollection(
            (
                IngredientQuantity(Ingredient.from_name("Baby Spinach"), Unit.GRAM, 200),
                IngredientQuantity(Ingredient.from_name("Cayenne Pepper"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Chicken Breast"), Unit.GRAM, 700),
                IngredientQuantity(Ingredient.from_name("Chicken Stock"), Unit.MILLILITRE, 250),
                IngredientQuantity(Ingredient.from_name("Cream"), Unit.MILLILITRE, 250),
                IngredientQuantity(Ingredient.from_name("Garlic Clove"), Unit.NUMBER, 3),
                IngredientQuantity(Ingredient.from_name("Mozarella Cheese"), Unit.GRAM, 100),
                IngredientQuantity(Ingredient.from_name("Parmesan Cheese"), Unit.GRAM, 100),
                IngredientQuantity(Ingredient.from_name("Penne Pasta"), Unit.GRAM, 300),
                IngredientQuantity(Ingredient.from_name("Sundried Tomatoes"), Unit.GRAM, 750),
            )
        ),
        properties={
            MealProperty.MEAT: MealMeat.CHICKEN,
        },
        tags=(MealTag.PASTA,),
    )
    PIZZA = Meal(
        name="Pizza",
        ingredient_quantities=IngredientQuantityCollection(
            (
                IngredientQuantity(Ingredient.from_name("Basil"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Caputo 00 Flour"), Unit.GRAM, 300),
                IngredientQuantity(Ingredient.from_name("Flour"), Unit.GRAM, 300),
                IngredientQuantity(Ingredient.from_name("Active Dry Yeast"), Unit.GRAM, 4),
                IngredientQuantity(Ingredient.from_name("Ham"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Honey"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Mozarella Cheese"), Unit.GRAM, 250),
                IngredientQuantity(Ingredient.from_name("Olive Oil"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Passata"), Unit.MILLILITRE, 250),
                IngredientQuantity(Ingredient.from_name("Pepperoni"), Unit.BOOL, True),
            )
        ),
        properties={
            MealProperty.MEAT: MealMeat.PORK,
        },
    )
    QUICHE_LORRAINE = Meal(
        name="Quiche Lorraine",
        ingredient_quantities=IngredientQuantityCollection(
            (
                IngredientQuantity(Ingredient.from_name("Bacon"), Unit.NUMBER, 8),
                IngredientQuantity(Ingredient.from_name("Cherry Tomatoes"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Double Cream"), Unit.MILLILITRE, 275),
                IngredientQuantity(Ingredient.from_name("Eggs"), Unit.NUMBER, 3),
                IngredientQuantity(Ingredient.from_name("Gruyere Cheese"), Unit.GRAM, 75),
                IngredientQuantity(Ingredient.from_name("Shortcrust Pastry"), Unit.BOOL, True),
            )
        ),
        properties={
            MealProperty.MEAT: MealMeat.PORK,
        },
    )
    ROAST_BEEF = Meal(
        name="Roast Beef",
        ingredient_quantities=IngredientQuantityCollection(
            (IngredientQuantity(Ingredient.from_name("Beef Joint"), Unit.BOOL, True),)
        ),
        properties={
            MealProperty.MEAT: MealMeat.BEEF,
        },
        tags=(MealTag.ROAST,),
    )
    ROAST_CHICKEN = Meal(
        name="Roast Chicken",
        ingredient_quantities=IngredientQuantityCollection(
            (IngredientQuantity(Ingredient.from_name("Whole Chicken"), Unit.BOOL, True),)
        ),
        properties={
            MealProperty.MEAT: MealMeat.CHICKEN,
        },
        tags=(MealTag.ROAST,),
    )
    ROAST_LAMB = Meal(
        name="Roast Lamb",
        ingredient_quantities=IngredientQuantityCollection(
            (IngredientQuantity(Ingredient.from_name("Leg of Lamb"), Unit.BOOL, True),)
        ),
        properties={
            MealProperty.MEAT: MealMeat.LAMB,
        },
        tags=(MealTag.ROAST,),
    )
    ROAST_PORK = Meal(
        name="Roast Pork",
        ingredient_quantities=IngredientQuantityCollection(
            (IngredientQuantity(Ingredient.from_name("Pork Joint"), Unit.BOOL, True),)
        ),
        properties={
            MealProperty.MEAT: MealMeat.PORK,
        },
        tags=(MealTag.ROAST,),
    )
    SAAG_PANEER = Meal(
        name="Saag Paneer",
        ingredient_quantities=IngredientQuantityCollection(
            (
                IngredientQuantity(Ingredient.from_name("Cayenne Pepper"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Coconut Milk"), Unit.MILLILITRE, 350),
                IngredientQuantity(Ingredient.from_name("Cumin"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Dried Fenugreek"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Garam Masala"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Garlic Clove"), Unit.NUMBER, 2),
                IngredientQuantity(Ingredient.from_name("Ghee"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Ginger"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Kosher Salt"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Onion"), Unit.NUMBER, 1),
                IngredientQuantity(Ingredient.from_name("Paneer Cheese"), Unit.GRAM, 350),
                IngredientQuantity(Ingredient.from_name("Spinach"), Unit.GRAM, 450),
                IngredientQuantity(Ingredient.from_name("Tumeric"), Unit.BOOL, True),
            )
        ),
        properties={
            MealProperty.MEAT: MealMeat.NONE,
        },
        tags=(MealTag.INDIAN,),
    )
    SHEPHERDS_PIE = Meal(
        name="Shepherds Pie",
        ingredient_quantities=IngredientQuantityCollection(
            (
                IngredientQuantity(Ingredient.from_name("Beef Mince"), Unit.GRAM, 500),
                IngredientQuantity(Ingredient.from_name("Beef Stock"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Butter"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Carrot"), Unit.NUMBER, 2),
                IngredientQuantity(Ingredient.from_name("Chopped Tomatoes"), Unit.NUMBER, 1),
                IngredientQuantity(Ingredient.from_name("Flour"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Lamb Mince"), Unit.GRAM, 500),
                IngredientQuantity(Ingredient.from_name("Olive Oil"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Onion"), Unit.NUMBER, 2),
                IngredientQuantity(Ingredient.from_name("Potato"), Unit.GRAM, 1000),
                IngredientQuantity(Ingredient.from_name("Red Wine"), Unit.MILLILITRE, 200),
                IngredientQuantity(Ingredient.from_name("Thyme"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Worcestershire Sauce"), Unit.BOOL, True),
            )
        ),
        properties={
            MealProperty.MEAT: MealMeat.BEEF,
        },
        tags=(MealTag.PASTA,),
    )
    SLOW_COOKER_BEEF_BOURGUIGNON = Meal(
        name="Slow Cooker Beef Bourgignon",
        ingredient_quantities=IngredientQuantityCollection(
            (
                IngredientQuantity(Ingredient.from_name("Bay Leaves"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Beef Broth"), Unit.MILLILITRE, 500),
                IngredientQuantity(Ingredient.from_name("Beef Chuck Steak"), Unit.GRAM, 900),
                IngredientQuantity(Ingredient.from_name("Butter"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Carrot"), Unit.NUMBER, 4),
                IngredientQuantity(Ingredient.from_name("Cipollini Onion"), Unit.GRAM, 450),
                IngredientQuantity(Ingredient.from_name("Dry Red Wine"), Unit.MILLILITRE, 700),
                IngredientQuantity(Ingredient.from_name("Flour"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Garlic Clove"), Unit.NUMBER, 2),
                IngredientQuantity(Ingredient.from_name("Kosher Salt"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Parsley"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Thick Cut Bacon"), Unit.GRAM, 300),
                IngredientQuantity(Ingredient.from_name("Thyme"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Tomato Puree"), Unit.GRAM, 50),
            )
        ),
        properties={
            MealProperty.MEAT: MealMeat.BEEF,
        },
    )
    SLOW_COOKER_CHICKEN_TIKKA_MASALA = Meal(
        name="Slow Cooker Chicken Tikka Masala",
        ingredient_quantities=IngredientQuantityCollection(
            (
                IngredientQuantity(Ingredient.from_name("Cayenne Pepper"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Chicken Breast"), Unit.NUMBER, 4),
                IngredientQuantity(Ingredient.from_name("Coriander"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Cumin"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Double Cream"), Unit.MILLILITRE, 250),
                IngredientQuantity(Ingredient.from_name("Garam Masala"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Garlic Clove"), Unit.NUMBER, 5),
                IngredientQuantity(Ingredient.from_name("Onion"), Unit.NUMBER, 1),
                IngredientQuantity(Ingredient.from_name("Rice"), Unit.GRAM, 500),
                IngredientQuantity(Ingredient.from_name("Tomato Puree"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Yogurt"), Unit.MILLILITRE, 250),
            )
        ),
        properties={
            MealProperty.MEAT: MealMeat.CHICKEN,
        },
        tags=(MealTag.INDIAN,),
    )
    SLOW_COOKER_HONEY_GARLIC_CHICKEN_AND_VEGGIES = Meal(
        name="Slow Cooker Honey Garlic Chicken and Veggies",
        ingredient_quantities=IngredientQuantityCollection(
            (
                IngredientQuantity(Ingredient.from_name("Baby Carrot"), Unit.GRAM, 450),
                IngredientQuantity(Ingredient.from_name("Baby Red Potato"), Unit.GRAM, 450),
                IngredientQuantity(Ingredient.from_name("Chicken Thigh"), Unit.NUMBER, 8),
                IngredientQuantity(Ingredient.from_name("Dried Basil"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Dried Oregano"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Garlic Clove"), Unit.NUMBER, 2),
                IngredientQuantity(Ingredient.from_name("Green Beans"), Unit.GRAM, 450),
                IngredientQuantity(Ingredient.from_name("Honey"), Unit.MILLILITRE, 100),
                IngredientQuantity(Ingredient.from_name("Ketchup"), Unit.MILLILITRE, 50),
                IngredientQuantity(Ingredient.from_name("Parsley"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Red Pepper Flakes"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Soy Sauce"), Unit.MILLILITRE, 100),
            )
        ),
        properties={
            MealProperty.MEAT: MealMeat.CHICKEN,
        },
    )
    SPAGHETTI_BOLOGNESE = Meal(
        name="Spaghetti Bolognese",
        ingredient_quantities=IngredientQuantityCollection(
            (
                IngredientQuantity(Ingredient.from_name("Bay Leaves"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Beef Mince"), Unit.GRAM, 500),
                IngredientQuantity(Ingredient.from_name("Carrot"), Unit.NUMBER, 1),
                IngredientQuantity(Ingredient.from_name("Celery"), Unit.NUMBER, 2),
                IngredientQuantity(Ingredient.from_name("Chopped Tomatoes"), Unit.NUMBER, 1),
                IngredientQuantity(Ingredient.from_name("Garlic Clove"), Unit.NUMBER, 3),
                IngredientQuantity(Ingredient.from_name("Mixed Herbs"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Onion"), Unit.NUMBER, 2),
                IngredientQuantity(Ingredient.from_name("Oregano"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Parmesan Cheese"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Pork Mince"), Unit.GRAM, 500),
                IngredientQuantity(Ingredient.from_name("Spaghetti"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Tomato Puree"), Unit.BOOL, True),
            )
        ),
        properties={
            MealProperty.MEAT: MealMeat.BEEF,
        },
        tags=(MealTag.PASTA,),
    )
    STICKY_CHINESE_PORK_BELLY = Meal(
        name="Sticky Chinese Pork Belly",
        ingredient_quantities=IngredientQuantityCollection(
            (
                IngredientQuantity(Ingredient.from_name("Brown Sugar"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Caster Sugar"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Chicken Stock"), Unit.MILLILITRE, 1000),
                IngredientQuantity(Ingredient.from_name("Dark Soy Sauce"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Garlic Clove"), Unit.NUMBER, 3),
                IngredientQuantity(Ingredient.from_name("Ginger"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Honey"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Lemongrass Paste"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Pork Belly Slice"), Unit.GRAM, 1000),
                IngredientQuantity(Ingredient.from_name("Red Chilli"), Unit.NUMBER, 2),
                IngredientQuantity(Ingredient.from_name("Rice Wine"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Rice"), Unit.GRAM, 500),
                IngredientQuantity(Ingredient.from_name("Vegetable Oil"), Unit.BOOL, True),
            )
        ),
        properties={
            MealProperty.MEAT: MealMeat.PORK,
        },
    )
    TURKEY_SWEET_POTATO_SHEPHERDS_PIE = Meal(
        name="Turkey Sweet Potato Shepherds Pie",
        ingredient_quantities=IngredientQuantityCollection(
            (
                IngredientQuantity(Ingredient.from_name("Carrot"), Unit.NUMBER, 2),
                IngredientQuantity(Ingredient.from_name("Celery"), Unit.NUMBER, 3),
                IngredientQuantity(Ingredient.from_name("Coconut Milk"), Unit.MILLILITRE, 150),
                IngredientQuantity(Ingredient.from_name("Coconut Oil"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Dried Thyme"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Garlic Powder"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Onion"), Unit.NUMBER, 1),
                IngredientQuantity(Ingredient.from_name("Oregano"), Unit.BOOL, True),
                IngredientQuantity(Ingredient.from_name("Sweet Potato"), Unit.NUMBER, 3),
                IngredientQuantity(Ingredient.from_name("Turkey Mince"), Unit.GRAM, 500),
            )
        ),
        properties={
            MealProperty.MEAT: MealMeat.TURKEY,
        },
    )
    TURKEY_STUFFED_PEPPERS = Meal(
        name="Turkey Stuffed Peppers",
        ingredient_quantities=IngredientQuantityCollection(
            (
                IngredientQuantity(Ingredient.from_name("Eggs"), Unit.NUMBER, 2),
                IngredientQuantity(Ingredient.from_name("Green Pepper"), Unit.NUMBER, 4),
                IngredientQuantity(Ingredient.from_name("Onion"), Unit.NUMBER, 2),
                IngredientQuantity(Ingredient.from_name("Passata"), Unit.MILLILITRE, 500),
                IngredientQuantity(Ingredient.from_name("Rice"), Unit.GRAM, 400),
                IngredientQuantity(Ingredient.from_name("Tomato Soup"), Unit.GRAM, 1),
                IngredientQuantity(Ingredient.from_name("Turkey Mince"), Unit.GRAM, 500),
            )
        ),
        properties={
            MealProperty.MEAT: MealMeat.TURKEY,
        },
    )


meal_names_to_meal_map = {x.value.name.upper(): x.value for x in Meals}
