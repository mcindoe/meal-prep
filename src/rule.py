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
from mealprep.src.meal import MealTag
from mealprep.src.meal import MealProperty


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
        assert date not in meal_diary.dates, f"{date.strftime('%Y-%m-%d')} is in the passed MealDiary"

        meal_collection = meal_collection.copy()
        ret = self.filter(meal_collection, date, meal_diary)
        assert isinstance(ret, MealCollection), f"Rule returned a {type(ret)}"

        return ret

    @staticmethod
    @abstractmethod
    def filter(meal_collection: MealCollection, date: dt.date, meal_diary: MealDiary) -> MealCollection:
        raise NotImplementedError("A Rule's filter method must be implemented")

    @staticmethod
    def from_name(rule_name: str):
        for rule in Rules:
            if rule.name.lower() == rule_name.lower():
                return rule.value
        raise ValueError(f'Could not find the rule "{rule_name}"')


class RuleCollection:
    def __init__(self, rules: Iterable[Rule]):
        self.rules = tuple(x for x in rules)
        assert all(isinstance(x, Rule) for x in self.rules)

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


class NotPastaTwiceWithinFiveDaysRule(Rule):
    @staticmethod
    def filter(meal_collection: MealCollection, date: dt.date, meal_diary: MealDiary) -> MealCollection:
        pasta_within_five_days = any(
            meal[MealTag.PASTA]
            for meal in meal_diary.filter_by_time_delta(date, dt.timedelta(days=5)).meals
        )

        if not pasta_within_five_days:
            return meal_collection

        return MealCollection(
            meal
            for meal in meal_collection.meals
            if not meal[MealTag.PASTA]
        )


# TODO: May require revisiting and changed to MealTemplates
class NotSameMealWithinSevenDaysRule(Rule):
    @staticmethod
    def filter(meal_collection: MealCollection, date: dt.date, meal_diary: MealDiary) -> MealCollection:
        meal_names_to_avoid = set(
            meal.name
            for meal in meal_diary.filter_by_time_delta(date, dt.timedelta(days=7)).meals
        )

        return MealCollection(
            meal
            for meal in meal_collection.meals
            if meal.name not in meal_names_to_avoid
        )


class NotSameMeatOnConsecutiveDaysRule(Rule):
    @staticmethod
    def filter(meal_collection: MealCollection, date: dt.date, meal_diary: MealDiary) -> MealCollection:
        meats_to_avoid = set(
            meal[MealProperty.MEAT]
            for meal in meal_diary.filter_by_time_delta(date, dt.timedelta(days=1)).meals
        )

        return MealCollection(
            meal
            for meal in meal_collection.meals
            if meal[MealProperty.MEAT] not in meats_to_avoid
        )


class Rules(BaseEnum):
    NOT_PASTA_TWICE_WITHIN_FIVE_DAYS = NotPastaTwiceWithinFiveDaysRule()
    NOT_SAME_MEAL_WITHIN_SEVEN_DAYS = NotSameMealWithinSevenDaysRule()
    NOT_SAME_MEAT_ON_CONSECUTIVE_DAYS = NotSameMeatOnConsecutiveDaysRule()
