"""
Provides the Meal class, functions to work with meal dictionaries, and
the meals data file
"""

import json
import random
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from mealprep.config import DATA
from mealprep.config import JSON_INDENT
from mealprep.src.utils.display import capitalise
from mealprep.src.utils.display import make_list_str

MEALS_FILE = DATA / "meals.json"


class Meal:
    """
    Describes a meal, with optional additions
    """

    def __init__(self, name: str, vegetables: Optional[List[str]] = None):
        self.name = name
        self.vegetables = vegetables

    def __repr__(self):
        if self.vegetables is None:
            return f"Meal({self.name})"
        return f"Meal({self.name}, {capitalise(self.vegetables)})"

    def __str__(self):
        if self.vegetables is None:
            return self.name
        return f"{self.name} with {capitalise(make_list_str(self.vegetables))}"

    @property
    def ingredients(self):
        meals = load_meals()

        ingredients = meals[self.name]["ingredients"]
        if self.vegetables is not None:
            for veg in self.vegetables:
                ingredients[veg] = True

        return ingredients

    def to_json(self):
        return {"name": self.name, "vegetables": self.vegetables}

    @staticmethod
    def from_json(meal_info):
        name = meal_info["name"]
        vegetables = meal_info["vegetables"]
        return Meal(name, vegetables)


def load_meals() -> Dict:
    """
    Load the dictionary of supported meals from file.
    """

    with open(MEALS_FILE, "r") as fp:
        meals = json.load(fp)
    return meals


def write_meals(meals: Dict) -> None:
    """
    Overwrite the meals data file with a dictionary of meals.
    """

    with open(MEALS_FILE, "w") as fp:
        json.dump(meals, fp, indent=JSON_INDENT)


def get_vegetables(meal: str) -> List[str]:
    """
    Return any vegetable choices which are associated with the specified
    meal. If not specified in the meals file, an empty list is returned.
    """

    meals = load_meals()

    if "vegetables" not in meals[meal].keys():
        return []
    return meals[meal]["vegetables"]


def choose_meal(meals: Dict[str, Dict]) -> Meal:
    """
    From the passed dictionary of meal information, choose a meal and
    make any additional choices about the meal (e.g. vegetables).
    """

    name = random.choice(list(meals.keys()))
    vegetables = get_vegetables(name)
    if not vegetables:
        return Meal(name)
    veg_choice = random.choice(vegetables)
    return Meal(name, [veg_choice])


def get_protein(meal_name: str) -> Union[None, str]:
    """
    Return the protein associated with the given meal choice
    """

    meals = load_meals()
    assert meal_name in meals.keys()

    if "protein" not in meals[meal_name].keys():
        return None
    return meals[meal_name]["protein"]


def is_fish(meal_name: str) -> bool:
    """
    Returns whether the specified meal name is registered as fish
    """

    return get_protein(meal_name) == "fish"


def is_attr(attr: str) -> Callable[[str], bool]:
    """
    Factory function to generate function which check if the specified
    meal name is registered as being of type 'attr'
    """

    def f(meal_name: str) -> bool:
        f"""
        Returns whether the specified meal name is registered as {attr}
        """
        meals = load_meals()
        assert meal_name in meals.keys()

        if attr not in meals[meal_name]:
            return False
        return meals[meal_name][attr]

    return f


is_pasta = is_attr("pasta")
is_roast = is_attr("roast")
is_favourite = is_attr("favourite")
is_time_consuming = is_attr("time-consuming")
