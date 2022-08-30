import collections
import copy
import datetime as dt
import json
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Iterable
from typing import Optional
from typing import Tuple
from typing import Union

from mealprep.src.basic_iterator import BasicIterator
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

PROJECT_DIARY_FILENAME = "meal_diary.json"
PROJECT_DIARY_FILEPATH = DATA_DIR / PROJECT_DIARY_FILENAME


class Meal:
    def __init__(
        self,
        name: str,
        ingredient_quantities: IngredientQuantityCollection,
        properties: Dict[MealProperty, Any],
        tags: Optional[Union[MealTag, Iterable[MealTag]]] = tuple()
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
                tags = (tags, )

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


class MealDiary:
    DATE_FORMAT = "%Y-%m-%d"

    def __init__(self, meal_diary: Optional[Dict[dt.date, Meal]] = None):
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

    def get_representation(self) -> Dict[str, str]:
        """
        Represent the instance as a dictionary mapping date strings to
        meal names
        """

        ret = {
            date.strftime(MealDiary.DATE_FORMAT): meal.name
            for date, meal in self.items()
        }
        return dict(sorted(ret.items()))

    def __repr__(self) -> str:
        return str(self.get_representation())

    def __bool__(self) -> bool:
        return len(self.meal_diary) > 0

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
        self.to_file(PROJECT_DIARY_FILEPATH)

    @staticmethod
    def from_project_diary() -> "MealDiary":
        return MealDiary.from_file(PROJECT_DIARY_FILEPATH)

    def upsert(self, other: "MealDiary") -> "MealDiary":
        return MealDiary(self.meal_diary | other.meal_diary)

    def difference(self, other: "MealDiary") -> "MealDiary":
        return MealDiary({
            date: meal
            for date, meal in self.meal_diary.items()
            if date not in other.meal_diary.keys()
        })

    def filter_by_time_delta(self, date: dt.date, time_delta: dt.timedelta) -> "MealDiary":
        return MealDiary({
            meal_date: meal
            for meal_date, meal in self.items()
            if abs(meal_date - date) <= time_delta
        })

    def except_dates(self, dates_to_exclude: Iterable[dt.date]) -> "MealDiary":
        """
        Return a copy of the MealDiary with the specified dates removed
        (if present)
        """

        if isinstance(dates_to_exclude, dt.date):
            dates_to_exclude = (dates_to_exclude, )

        dates_to_exclude = set(x for x in dates_to_exclude)

        if not all(isinstance(x, dt.date) for x in dates_to_exclude):
            raise TypeError("All passed dates must be datetime.dates")

        return MealDiary({
            meal_date: meal
            for meal_date, meal in self.items()
            if meal_date not in dates_to_exclude
        })

    @staticmethod
    def get_pretty_print_date_string(
        date: dt.date,
        include_date_number_spacing: bool = False,
        include_year: bool = False
    ) -> str:
        """
        Get a representation of a date object as, e.g., Wed 5th Jan 22.

        Args:
        include_date_number_spacing: whether to ensure that the date
            number portion of the returned string has two characters, by
            left-padding numbers less than 10 with a space
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

    def get_pretty_print_string(self) -> str:
        include_date_number_spacing = any(x.day >= 10 for x in self.dates)
        include_year = len(set(x.year for x in self.dates)) > 1

        lines = []
        for date, meal in self.items():
            date_str = self.get_pretty_print_date_string(date, include_date_number_spacing, include_year)
            lines.append(f"{date_str}: {meal.name}")

        return "\n".join(lines)


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
            MealProperty.MEAT: MealMeat.BEEF
        }
    )
    BURGERS = Meal(
        name="Burgers",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.BACON, Unit.BOOL, True),
            IngredientQuantity(Ingredients.BEEF_CHUCK_STEAK, Unit.GRAM, 450),
            IngredientQuantity(Ingredients.BURGER_BUNS, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.CHEDDAR_CHEESE, Unit.BOOL, True),
            IngredientQuantity(Ingredients.DRIED_MUSTARD, Unit.BOOL, True),
            IngredientQuantity(Ingredients.EGGS, Unit.BOOL, True),
            IngredientQuantity(Ingredients.LETTUCE, Unit.BOOL, True),
            IngredientQuantity(Ingredients.MAYONNAISE, Unit.BOOL, True),
            IngredientQuantity(Ingredients.ONION, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.TOMATO, Unit.BOOL, True),
        ),
        properties={
            MealProperty.MEAT: MealMeat.BEEF
        }
    )
    CHICKEN_FAJITAS = Meal(
        name="Chicken Fajitas",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.CHICKEN_BREAST, Unit.GRAM, 400),
            IngredientQuantity(Ingredients.CORIANDER, Unit.BOOL, True),
            IngredientQuantity(Ingredients.PAPRIKA, Unit.BOOL, True),
            IngredientQuantity(Ingredients.RED_ONION, Unit.NUMBER, 2),
            IngredientQuantity(Ingredients.RED_PEPPER, Unit.NUMBER, 1),
            IngredientQuantity(Ingredients.TORTILLA_WRAP, Unit.NUMBER, 8),
            IngredientQuantity(Ingredients.YELLOW_PEPPER, Unit.NUMBER, 1),
        ),
        properties={
            MealProperty.MEAT: MealMeat.CHICKEN
        }
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
            MealProperty.MEAT: MealMeat.CHICKEN
        }
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
            MealProperty.MEAT: MealMeat.CHICKEN
        }
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
            MealProperty.MEAT: MealMeat.CHICKEN
        }
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
            MealProperty.MEAT: MealMeat.BEEF
        }
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
            MealProperty.MEAT: MealMeat.FISH
        }
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
            MealProperty.MEAT: MealMeat.FISH
        }
    )
    INDIAN_LAMB_WITH_SPICED_LENTILS = Meal(
        name="Indian Lamb with Spiced Lentils",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.BONELESS_LEG_OF_LAMB, Unit.GRAM, 500),
            IngredientQuantity(Ingredients.CARDAMOM, Unit.BOOL, True),
            IngredientQuantity(Ingredients.CINAMMON_STICKS, Unit.NUMBER, 1),
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
            MealProperty.MEAT: MealMeat.LAMB
        }
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
            MealProperty.MEAT: MealMeat.FISH
        }
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
            MealProperty.MEAT: MealMeat.BEEF
        }
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
            MealProperty.MEAT: MealMeat.LAMB
        }
    )
    PASTA_WITH_CHICKEN_AND_SUNDRIED_TOMATOES = Meal(
        name="Pasta with Chicken and Sundried Tomatoes",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.BABY_SPINACH, Unit.GRAM, 200),
            IngredientQuantity(Ingredients.CAYENNE_PEPPER, Unit.BOOL, True),
            IngredientQuantity(Ingredients.CHICKEN_BREAST, Unit.GRAM, 700),
            IngredientQuantity(Ingredients.CHICKEN_STOCK, Unit.GRAM, 250),
            IngredientQuantity(Ingredients.CREAM, Unit.MILLILITRE, 250),
            IngredientQuantity(Ingredients.GARLIC_CLOVE, Unit.NUMBER, 3),
            IngredientQuantity(Ingredients.MOZARELLA_CHEESE, Unit.GRAM, 100),
            IngredientQuantity(Ingredients.PARMESAN_CHEESE, Unit.GRAM, 100),
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
            MealProperty.MEAT: MealMeat.PORK
        },
    )
    ROAST_BEEF = Meal(
        name="Roast Beef",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.BEEF_JOINT, Unit.BOOL, True),
        ),
        properties={
            MealProperty.MEAT: MealMeat.BEEF
        },
        tags=(
            MealTag.ROAST,
        )
    )
    ROAST_CHICKEN = Meal(
        name="Roast Chicken",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.WHOLE_CHICKEN, Unit.BOOL, True),
        ),
        properties={
            MealProperty.MEAT: MealMeat.CHICKEN
        },
        tags=(
            MealTag.ROAST,
        )
    )
    ROAST_LAMB = Meal(
        name="Roast Lamb",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.LEG_OF_LAMB, Unit.BOOL, True),
        ),
        properties={
            MealProperty.MEAT: MealMeat.LAMB
        },
        tags=(
            MealTag.ROAST,
        )
    )
    ROAST_PORK = Meal(
        name="Roast Pork",
        ingredient_quantities=(
            IngredientQuantity(Ingredients.PORK_JOINT, Unit.BOOL, True),
        ),
        properties={
            MealProperty.MEAT: MealMeat.PORK
        },
        tags=(
            MealTag.ROAST,
        )
    )
    SHEPHARDS_PIE = Meal(
        name="Shephards Pie",
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
            MealProperty.MEAT: MealMeat.BEEF
        },
        tags=(
            MealTag.PASTA,
        )
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
