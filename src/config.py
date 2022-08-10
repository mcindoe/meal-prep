from typing import Any, Dict, List
import yaml

from mealprep.src.constants import ConfigEntries


class Config:
    def __init__(self) -> None:
        with open("/home/conor/Programming/mealprep/config.yaml", "r") as fp:
            self.config: Dict[Any, Any] = yaml.load(fp, yaml.SafeLoader)

    @property
    def email_addresses(self) -> List:
        return self.config[ConfigEntries.EMAIL_ADDRESSES.value]


config = Config()
