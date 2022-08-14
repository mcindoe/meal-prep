from abc import ABC
from abc import abstractmethod
import re
from typing import Any
from typing import Iterable
from typing import Tuple
from typing import Union


class UserInputGetter(ABC):
    EXIT_SIGNAL = "Q"

    REQUEST_VALUE_MESSAGE = "Enter value"
    COULD_NOT_PARSE_MESSAGE = "Could not parse input"
    NOT_SUPPORTED_MESSAGE = "Unsupported option passed"

    MULTIPLE_REQUEST_VALUE_MESSAGE = "Enter values, separated by a comma"
    MULTIPLE_COULD_NOT_PARSE_MESSAGE = "Could not parse inputs"
    MULTIPLE_NOT_SUPPORTED_MESSAGE = "Unsupported options passed"

    def __init__(self, supported_options: Union[None, Iterable[Any]] = None):
        if supported_options is None:
            self.supported_options = None
        else:
            self.supported_options = {x for x in supported_options}

    def is_supported(self, value: Any) -> bool:
        if self.supported_options is None:
            return True

        return value in self.supported_options

    def is_exit_signal(self, value: str) -> bool:
        return value.lower() == UserInputGetter.EXIT_SIGNAL.lower()

    @staticmethod
    def is_valid(value: str) -> bool:
        """Check that conversion to the required type makes sense"""
        return True

    @staticmethod
    def parse(value: str) -> str:
        "Conversion from string to required type"
        return value

    def get_input(self) -> Any:
        """
        Keep attempting to retrieve a user input, parseable and in the
        set of supported results (if specified), until successful. Exit
        if an EXIT_SIGNAL is passed. Return None if unsuccessful
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

    def get_multiple_inputs(self) -> Tuple[Any]:

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
    regex = re.compile("^[-+]?[0-9]+$")

    def __init__(self, supported_options: Union[None, Iterable[int]] = None):
        super().__init__(supported_options)

    @staticmethod
    def is_valid(value) -> bool:
        return bool(IntegerInputGetter.regex.match(value))

    @staticmethod
    def parse(value: str) -> int:
        return int(value)


StringInputGetter = UserInputGetter
