from abc import ABC
from abc import abstractmethod
import copy
import datetime as dt
from typing import Iterable

from mealprep.src.constants import BaseEnum
from mealprep.src.constants import Category
from mealprep.src.meal import Meal
from mealprep.src.meal import MealCollection
from mealprep.src.meal import MealDiary


class Rule(ABC):
    """
    A Rule is a file which can be applied to a MealCollection, with a MealDiary as context,
    to find a smaller MealCollection which don't violate the rule, on the date, given that
    MealDiary
    """

    def __call__(
        self,
        meal_collection: MealCollection,
        date: dt.date,
        meal_diary: MealDiary
    ) -> MealCollection:

        assert isinstance(meal_collection, MealCollection)
        assert isinstance(meal_diary, MealDiary), f"Rule was pased a {type(meal_diary)}"

        meal_collection = meal_collection.copy()
        ret = self.filter(meal_collection, date, meal_diary)
        assert isinstance(ret, MealCollection), f"Rule returned a {type(ret)}"

        return ret

    @staticmethod
    @abstractmethod
    def filter(meal_collection: MealCollection, date: dt.date, meal_diary: MealDiary) -> MealCollection:
        raise NotImplementedError("A Rule's filter method must be implemented")


class RuleCollection:
    def __init__(self, rules: Iterable[Rule]):
        self.rules = tuple(x for x in rules)
        assert all(issubclass(x, Rule) for x in self.rules)

    def copy(self) -> "RuleCollection":
        return RuleCollection(copy.deepcopy(self.rules))

    def __call__(
        self,
        meal_collection: MealCollection,
        date: dt.date,
        meal_diary: MealDiary
    ) -> MealCollection:

        ret = meal_collection
        for rule in self.rules:
            ret = rule(ret, date, meal_diary)
        return ret


# TODO: This just an example. Something we can implement when setting up the project
class NoVegetablesRule(Rule):
    @staticmethod
    def filter(meal_collection: MealCollection, date: dt.date, meal_diary: MealDiary) -> MealCollection:
        return MealCollection(
            x for x in meal_collection.meals
            if not any(ing.category == Category.VEGETABLE for ing in x.ingredient_quantities)
        )


class Rules(BaseEnum):
    NO_VEGETABLES = NoVegetablesRule()
