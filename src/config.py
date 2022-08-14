import datetime as dt
from pathlib import Path
from typing import Any, Dict, Tuple
import yaml

from mealprep.src.constants import ConfigEntries


def parse_date_from_string(date_str: str) -> dt.date:
    separators = ("-", "/", " ")

    date_str = date_str.strip()
    for s in separators:
        date_str = date_str.replace(s, "")

    try:
        year = int(date_str[:4])
        month = int(date_str[4:6])
        day = int(date_str[6:])

        return dt.date(year, month, day)

    except Exception as e:
        raise ValueError(f"Unable to parse {date_str} as a date")


class Config:
    def __init__(self) -> None:
        with open("/home/conor/Programming/mealprep/config.yaml", "r") as fp:
            self.config: Dict[Any, Any] = yaml.load(fp, yaml.SafeLoader)

    @property
    def email_addresses(self) -> Tuple[str]:
        return self.config[ConfigEntries.EMAIL_ADDRESSES.value]

    @property
    def dates(self) -> Tuple[dt.date]:
        date_strings = self.config[ConfigEntries.DATES.value]
        return tuple(parse_date_from_string(x) for x in date_strings)


config = Config()

MEALPREP_ROOT_DIR = Path("/home/conor/Programming/mealprep")
MEALPREP_DATA_DIR = MEALPREP_ROOT_DIR / "data"
