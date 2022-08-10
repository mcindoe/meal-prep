from abc import ABC
from abc import abstractmethod
import re
from typing import Any
from typing import Iterable


class UserInputGetter(ABC):
    EXIT_SIGNAL = "Q"

    def __init__(
        self,
        supported_options: Iterable[Any],
        request_value_message="Enter value",
        could_not_parse_message="Could not parse input",
        not_supported_message="Unsupported option passed"
    ):
        self.supported_options = {x for x in supported_options}
        self.request_value_message = f"{request_value_message} ({UserInputGetter.EXIT_SIGNAL} to quit): "
        self.could_not_parse_message = could_not_parse_message
        self.not_supported_message = f"{not_supported_message}. Supported: {list(self.supported_options)}"

    def is_supported(self, value: Any) -> bool:
        return value in self.supported_options

    def is_exit_signal(self, value: str) -> bool:
        return value.lower().strip() == UserInputGetter.EXIT_SIGNAL.lower()

    @staticmethod
    @abstractmethod
    def is_valid(value: str) -> bool:
        raise NotImplementedError("is_valid must be implemented in subclasses of UserInputGetter")

    @staticmethod
    def parse(value: str) -> str:
        "Conversion from string to required type"
        return value

    def get_input(self) -> Any:
        """
        Keep attempting to retrieve a user input, parseable and in the
        set of supported results, until successful. Exit if an EXIT_SIGNAL
        is passed. Return None if unsuccessful
        """

        while True:
            # Get a valid value. Exit on EXIT_SIGNAL
            while True:
                inp = input(self.request_value_message)

                if self.is_exit_signal(inp):
                    return

                if self.is_valid(inp):
                    inp = self.parse(inp)
                    break

                print(self.could_not_parse_message)

            if self.is_supported(inp):
                return inp

            print(self.not_supported_message)


class IntegerInputGetter(UserInputGetter):
    regex = re.compile("^[-+]?[0-9]+$")

    def __init__(self, supported_options: Iterable[int]):
        super().__init__(supported_options)

    @staticmethod
    def is_valid(value) -> bool:
        return bool(IntegerInputGetter.regex.match(value))

    @staticmethod
    def parse(value: str) -> int:
        return int(value)
