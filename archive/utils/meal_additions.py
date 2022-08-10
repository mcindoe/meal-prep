"""
Provides functions to interact with files specifying the supported
meal additions, which include extras, vegetables, sides and additionals
"""

from typing import Dict
from typing import List
import json

from mealprep.config import DATA

EXTRAS_FILE = DATA / "extras.json"


def load_extras() -> Dict:
    """
    Load the extras dictionary from file
    """

    with open(EXTRAS_FILE, "r") as fp:
        extras = json.load(fp)
    return extras


def load_vegetables() -> List:
    """
    Load the vegetables list from file
    """

    extras = load_extras()
    return extras["vegetables"]


def load_sides() -> Dict:
    """
    Load the sides dictionary from file
    """

    extras = load_extras()
    return extras["sides"]


def load_additionals() -> List:
    """
    Load the additionals list from file
    """

    extras = load_extras()
    return extras["additionals"]
