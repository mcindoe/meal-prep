from abc import ABC, abstractmethod
import copy
import datetime as dt
from typing import Iterable

from mealprep.basic_iterator import BasicIterator
from mealprep.constants import BaseEnum, MealMeat
from mealprep.meal import Meal, MealProperty, MealTag
from mealprep.meal_collection import MealCollection
from mealprep.meal_diary import MealDiary


class Rule(ABC):
    """
    A Rule is a file which can be applied to a MealCollection, with a MealDiary as context,
    to find a smaller MealCollection which don't violate the rule, on the date, given that
    MealDiary
    """

    def __call__(
        self, meal_collection: MealCollection, date: dt.date, meal_diary: MealDiary
    ) -> MealCollection:
        if not isinstance(meal_collection, MealCollection):
            raise TypeError("'meal_collection' parameter must be a MealCollection")

        if not isinstance(meal_diary, MealDiary):
            raise TypeError(f"'meal_diary' parameter must be a MealDiary")

        if date in meal_diary.dates:
            raise ValueError(
                f"Rule was passed a date, {date.strftime('%Y-%m-%d')}, which is already in the passed MealDiary"
            )

        meal_collection = meal_collection.copy()
        ret = self.filter(meal_collection, date, meal_diary)

        if not isinstance(ret, MealCollection):
            raise TypeError(f"Rule returned a type {type(ret)} instead of a MealCollection")

        return ret

    @staticmethod
    @abstractmethod
    def filter(
        meal_collection: MealCollection, date: dt.date, meal_diary: MealDiary
    ) -> MealCollection:
        raise NotImplementedError("A Rule's filter method must be implemented")

    @staticmethod
    def from_name(rule_name: str) -> "Rule":
        for rule in Rules:
            if rule.name.lower() == rule_name.lower():
                return rule.value

        raise ValueError(f'Could not find the rule "{rule_name}"')


class RuleCollection:
    def __init__(self, rules: Iterable[Rule]):
        self.rules = tuple(x for x in rules)
        if not all(isinstance(x, Rule) for x in self.rules):
            raise TypeError("RuleCollection init was passed an element which is not a Rule")

    def copy(self) -> "RuleCollection":
        return RuleCollection(copy.copy(self.rules))

    def append(self, rule: Rule) -> "RuleCollection":
        if not isinstance(rule, Rule):
            raise TypeError("'rule' argument must be a Rule in RuleCollection.append")

        return RuleCollection(self.rules + (rule,))

    def __iter__(self) -> BasicIterator:
        return BasicIterator(self.rules)

    def __call__(
        self, meal_collection: MealCollection, date: dt.date, meal_diary: MealDiary
    ) -> MealCollection:
        ret = meal_collection
        for rule in self:
            ret = rule(ret, date, meal_diary)
        return ret


class ForceRoastOnSunday(Rule):
    @staticmethod
    def filter(
        meal_collection: MealCollection, date: dt.date, meal_diary: MealDiary
    ) -> MealCollection:
        if date.weekday() != 6:
            return meal_collection

        return MealCollection(meal for meal in meal_collection if meal[MealTag.ROAST])


class NotIndianTwiceWithinTenDaysRule(Rule):
    @staticmethod
    def filter(
        meal_collection: MealCollection, date: dt.date, meal_diary: MealDiary
    ) -> MealCollection:
        indian_within_ten_days = any(
            meal[MealTag.INDIAN]
            for meal in meal_diary.filter_by_time_delta(date, dt.timedelta(days=10)).meals
        )

        if not indian_within_ten_days:
            return meal_collection

        return MealCollection(meal for meal in meal_collection if not meal[MealTag.INDIAN])


class NotPastaTwiceWithinFiveDaysRule(Rule):
    @staticmethod
    def filter(
        meal_collection: MealCollection, date: dt.date, meal_diary: MealDiary
    ) -> MealCollection:
        pasta_within_five_days = any(
            meal[MealTag.PASTA]
            for meal in meal_diary.filter_by_time_delta(date, dt.timedelta(days=5)).meals
        )

        if not pasta_within_five_days:
            return meal_collection

        return MealCollection(meal for meal in meal_collection if not meal[MealTag.PASTA])


class NotRoastOnNonSunday(Rule):
    @staticmethod
    def filter(
        meal_collection: MealCollection, date: dt.date, meal_diary: MealDiary
    ) -> MealCollection:
        if date.weekday() == 6:
            return meal_collection

        return MealCollection(meal for meal in meal_collection if not meal[MealTag.ROAST])


class NotSameMealWithinSevenDaysRule(Rule):
    @staticmethod
    def filter(
        meal_collection: MealCollection, date: dt.date, meal_diary: MealDiary
    ) -> MealCollection:
        meal_names_to_avoid = set(
            meal.name for meal in meal_diary.filter_by_time_delta(date, dt.timedelta(days=7)).meals
        )

        return MealCollection(
            meal for meal in meal_collection if meal.name not in meal_names_to_avoid
        )


class NotSameMeatOnConsecutiveDaysRule(Rule):
    @staticmethod
    def filter(
        meal_collection: MealCollection, date: dt.date, meal_diary: MealDiary
    ) -> MealCollection:
        meats_to_avoid = set(
            meal[MealProperty.MEAT]
            for meal in meal_diary.filter_by_time_delta(date, dt.timedelta(days=1)).meals
            if meal[MealProperty.MEAT] is not MealMeat.NONE
        )

        return MealCollection(
            meal for meal in meal_collection if meal[MealProperty.MEAT] not in meats_to_avoid
        )


class NotSpecifiedMealOnSpecifiedDate(Rule):
    def __init__(self, date: dt.date, meal_to_avoid: Meal):
        if not isinstance(date, dt.date):
            raise TypeError(
                "'date' argument must be a datetime.date in NotSpecifiedMealOnSpecifiedDate init"
            )
        if not isinstance(meal_to_avoid, Meal):
            raise TypeError(
                "'meal_to_avoid' argument must be a Meal in NotSpecifiedMealOnSpecifiedDate init"
            )

        self.date = date
        self.meal_to_avoid = meal_to_avoid

    def filter(
        self, meal_collection: MealCollection, date: dt.date, meal_diary: MealDiary
    ) -> MealCollection:
        if date != self.date:
            return meal_collection

        return MealCollection(meal for meal in meal_collection if meal != self.meal_to_avoid)


class Rules(BaseEnum):
    FORCE_ROAST_ON_SUNDAY = ForceRoastOnSunday()
    NOT_INDIAN_TWICE_WITHIN_TEN_DAYS = NotIndianTwiceWithinTenDaysRule()
    NOT_PASTA_TWICE_WITHIN_FIVE_DAYS = NotPastaTwiceWithinFiveDaysRule()
    NOT_ROAST_ON_NON_SUNDAY = NotRoastOnNonSunday()
    NOT_SAME_MEAL_WITHIN_SEVEN_DAYS = NotSameMealWithinSevenDaysRule()
    NOT_SAME_MEAT_ON_CONSECUTIVE_DAYS = NotSameMeatOnConsecutiveDaysRule()
