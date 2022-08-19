import datetime as dt
from typing import Any, Dict, Tuple
import yaml

from mealprep.src.constants import ConfigEntries
from mealprep.src.loc import ROOT_DIR
from mealprep.src.rule import Rule
from mealprep.src.rule import RuleCollection

config_filepath = ROOT_DIR / "config.yaml"


class Config:
    def __init__(self) -> None:
        with open(config_filepath, "r") as fp:
            self.config: Dict[Any, Any] = yaml.load(fp, yaml.SafeLoader)

    @property
    def email_addresses(self) -> Tuple[str]:
        # TODO: Add a regexp and check that email entries are valid
        return tuple(self.config[ConfigEntries.EMAIL_ADDRESSES.value])

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
