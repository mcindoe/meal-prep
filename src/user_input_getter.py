"""
Provides a hierarchy of classes which get and parse user input.

There is some understanding of the type to cast the user input string
into, and (optionally) a set of supported options. The getter will
continuously prompt the user for a parsable, supported option until one
is provided, or until an exit signal is passed.

If no supported options are provided, then any parsable input is accepted
"""


from abc import ABC
import datetime as dt
import itertools
import functools
import re
from typing import Any
from typing import Iterable
from typing import Optional
from typing import Tuple
from typing import Union

from mealprep.src.utils import get_day_suffix


class UserInputGetter(ABC):
    EXIT_SIGNAL = "Q"

    REQUEST_VALUE_MESSAGE = "Enter value"
    COULD_NOT_PARSE_MESSAGE = "Could not parse input"
    NOT_SUPPORTED_MESSAGE = "Unsupported option passed"

    MULTIPLE_REQUEST_VALUE_MESSAGE = "Enter values, separated by a comma"
    MULTIPLE_COULD_NOT_PARSE_MESSAGE = "Could not parse inputs"
    MULTIPLE_NOT_SUPPORTED_MESSAGE = "Unsupported options passed"

    def __init__(self, supported_options: Optional[Iterable[Any]] = None):
        if supported_options is None:
            self.supported_options = None
        else:
            self.supported_options = {x for x in supported_options}

    def is_supported(self, value: Any) -> bool:
        """
        Check that the parsed input is a supported option. Typically this
        will not need to be overloaded
        """

        if self.supported_options is None:
            return True

        return value in self.supported_options

    def is_exit_signal(self, value: str) -> bool:
        return value.lower() == UserInputGetter.EXIT_SIGNAL.lower()

    @staticmethod
    def is_valid(value: str) -> bool:
        """
        Check that conversion to the required type makes sense
        """

        return True

    @staticmethod
    def parse(value: str) -> str:
        """
        Convert the user input from string to the required type
        """

        return value

    def get_input(self) -> Any:
        """
        Keep attempting to retrieve a user input, parseable and in the
        set of supported results (if specified), until successful. Return
        None if an EXIT_SIGNAL is sent from the user
        """

        request_value_message = f"{self.REQUEST_VALUE_MESSAGE} ({UserInputGetter.EXIT_SIGNAL} to quit): "

        while True:
            # Keep requesting input until a parsable value or EXIT_SIGNAL is passed
            while True:
                inp = input(request_value_message)
                inp = inp.strip()

                if self.is_exit_signal(inp):
                    return

                if self.is_valid(inp):
                    inp = self.parse(inp)
                    break

                print(self.COULD_NOT_PARSE_MESSAGE)

            if self.is_supported(inp):
                return inp

            print(self.NOT_SUPPORTED_MESSAGE)

    def get_multiple_inputs(self) -> Union[None, Tuple[Any]]:
        """
        Similar to get_input(), but get multiple values separated by commas
        """

        request_value_message = (
            f"{self.MULTIPLE_REQUEST_VALUE_MESSAGE} ({UserInputGetter.EXIT_SIGNAL} to quit): "
        )

        while True:
            # Keep requesting input until a parsable value or EXIT_SIGNAL is passed
            while True:
                inp = input(request_value_message)
                inp = inp.strip()

                if self.is_exit_signal(inp):
                    return

                inp = tuple(x.strip() for x in inp.split(","))

                if all(self.is_valid(x) for x in inp):
                    inp = tuple(self.parse(x) for x in inp)
                    break

                bad_input_values = tuple(x for x in inp if not self.is_valid(x))
                could_not_parse_message = (
                    f"{self.MULTIPLE_COULD_NOT_PARSE_MESSAGE}. Bad values: {bad_input_values}"
                )
                print(could_not_parse_message)

            if all(self.is_supported(x) for x in inp):
                return inp

            unsupported_values = tuple(x for x in inp if not self.is_supported(x))
            not_supported_message = (
                f"{self.MULTIPLE_NOT_SUPPORTED_MESSAGE}. Unsupported values: {unsupported_values}\n"
                f"Supported options: {tuple(self.supported_options)}"
            )
            print(not_supported_message)


class IntegerInputGetter(UserInputGetter):
    regex = re.compile("^([-+]?[1-9][0-9]*|0)$")

    def __init__(self, supported_options: Optional[Iterable[int]] = None):
        if supported_options is not None:
            supported_options = tuple(x for x in supported_options)
            if not all(isinstance(x, int) for x in supported_options):
                raise TypeError("All supported options, if specified, must be integers")

        super().__init__(supported_options)

    @staticmethod
    def is_valid(value) -> bool:
        return bool(IntegerInputGetter.regex.match(value))

    @staticmethod
    def parse(value: str) -> int:
        return int(value)


class CaseInsensitiveStringInputGetter(UserInputGetter):
    def __init__(self, supported_options: Optional[Iterable[str]] = None):
        if supported_options is not None:
            supported_options = tuple(x for x in supported_options)
            if not all(isinstance(x, str) for x in supported_options):
                raise TypeError("All supported options, if specified, must be strings")

        super().__init__(supported_options)

    def is_supported(self, value: Any) -> bool:
        if self.supported_options is None:
            return True

        return any(value.lower() == x.lower() for x in self.supported_options)

    def parse(self, value: str) -> int:
        if self.supported_options is None:
            return value

        # If possible, match the case of another otherwise-matching entry
        for option in self.supported_options:
            if option.lower() == value.lower():
                return option

        # If not possible, pass the value on unchanged to be flagged as not supported
        return value


def format_date_string(date, fmt):
    return date.strftime(fmt)


class DateInputGetter(UserInputGetter):
    DATE_FORMATS = (
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%Y%m%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%d%m%Y",
        "%d-%m",
    )

    DATE_TO_STRING_MAPS = tuple(
        functools.partial(format_date_string, fmt=date_format)
        for date_format in DATE_FORMATS
    )

    DATE_TO_STRING_MAPS += (
        lambda date: f"{date.day}{get_day_suffix(date.day)}",
        lambda date: str(date.day),
        lambda date: date.strftime("%A"),
        lambda date: date.strftime("%A")[:3]
    )

    def __init__(self, supported_options: Iterable[dt.date]):
        supported_options = tuple(x for x in supported_options)
        if not all(isinstance(x, dt.date) for x in supported_options):
            raise TypeError("All supported options must be datetime.dates")

        super().__init__(supported_options)

        if len(self.supported_options) == 0:
            raise ValueError("DateInputGetter must be passed supported options")

        self.lookup_map = {}
        for idx, date_to_string_map in enumerate(DateInputGetter.DATE_TO_STRING_MAPS):
            string_to_date_map = {
                date_to_string_map(date): date
                for date in self.supported_options
            }

            # This representation of dates as strings only makes sense if it's a bijection
            if len(string_to_date_map) == len(self.supported_options):
                if any(k in self.lookup_map for k in string_to_date_map):
                    raise ValueError("Found an unexpected lookup map collision")

                self.lookup_map |= string_to_date_map

    def is_valid(self, value) -> bool:
        return value in self.lookup_map

    def parse(self, value: str) -> dt.date:
        return self.lookup_map[value]
