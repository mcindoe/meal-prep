import datetime as dt
import re
from typing import Tuple

import yaml

from mealprep.constants import ConfigEntries
from mealprep.loc import ROOT_DIR
from mealprep.meal import Meal, MealCollection
from mealprep.rule import Rule, RuleCollection


config_filepath = ROOT_DIR / "mealprep/config.yaml"


class Config:
    email_address_regex = re.compile(r"^[A-Z0-9._%+-]+@[A-Z0-9.-]+.[A-Z]{2,}$", re.IGNORECASE)

    def __init__(self) -> None:
        with open(config_filepath, "r") as fp:
            self.config = yaml.load(fp, yaml.SafeLoader)

    @property
    def email_addresses(self) -> Tuple[str, ...]:
        ret = tuple(self.config[ConfigEntries.EMAIL_ADDRESSES.value])

        bad_addresses = tuple(x for x in ret if not self.email_address_regex.match(x))
        if bad_addresses:
            raise ValueError(f"Bad email addresses in project config: {bad_addresses}")

        return ret

    @property
    def dates(self) -> Tuple[dt.date, ...]:
        ret = tuple(self.config[ConfigEntries.DATES.value])
        if not all(isinstance(x, dt.date) for x in ret):
            raise ValueError("Not all config date entries are in the correct format")
        return ret

    @property
    def meals(self) -> Tuple[Meal, ...]:
        meal_names = tuple(self.config[ConfigEntries.MEALS.value])
        return tuple(Meal.from_name(x) for x in meal_names)

    @property
    def meal_collection(self) -> MealCollection:
        return MealCollection(self.meals)

    @property
    def rules(self) -> Tuple[Rule, ...]:
        rule_names = tuple(self.config[ConfigEntries.RULES.value])
        return tuple(Rule.from_name(x) for x in rule_names)

    @property
    def rule_collection(self) -> RuleCollection:
        return RuleCollection(self.rules)


config = Config()
