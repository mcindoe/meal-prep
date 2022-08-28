import datetime as dt
import re
from typing import Tuple
import yaml

from mealprep.src.constants import ConfigEntries
from mealprep.src.loc import ROOT_DIR
from mealprep.src.rule import Rule
from mealprep.src.rule import RuleCollection

config_filepath = ROOT_DIR / "config.yaml"


class Config:
    email_address_regex = re.compile("^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$", re.IGNORECASE)

    def __init__(self) -> None:
        with open(config_filepath, "r") as fp:
            self.config = yaml.load(fp, yaml.SafeLoader)

    @property
    def email_addresses(self) -> Tuple[str]:
        ret = tuple(self.config[ConfigEntries.EMAIL_ADDRESSES.value])

        bad_addresses = tuple(x for x in ret if not self.email_address_regex.match(x))
        if bad_addresses:
            raise ValueError(f"Bad email addresses in project config: {bad_addresses}")

        return ret

    @property
    def dates(self) -> Tuple[dt.date]:
        ret = tuple(self.config[ConfigEntries.DATES.value])
        if not all(isinstance(x, dt.date) for x in ret):
            raise ValueError("Not all config date entries are in the correct format")
        return ret

    @property
    def rules(self) -> Tuple[Rule]:
        rule_names = tuple(self.config[ConfigEntries.RULES.value])
        return tuple(Rule.from_name(x) for x in rule_names)

    @property
    def rule_collection(self) -> RuleCollection:
        return RuleCollection(self.rules)


config = Config()
