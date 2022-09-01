import datetime as dt
import pytest

from mealprep.src.user_input_getter import IntegerInputGetter
from mealprep.src.user_input_getter import CaseInsensitiveStringInputGetter
from mealprep.src.user_input_getter import DateInputGetter


class TestIntegerInputGetter:
    @pytest.fixture()
    def any_integer_input_getter(self):
        yield IntegerInputGetter()

    @pytest.fixture()
    def supported_options(self):
        yield (42, 100, 142)

    @pytest.fixture()
    def unsupported_options(self):
        yield (200, -42)

    @pytest.fixture()
    def specified_integer_input_getter(self, supported_options):
        yield IntegerInputGetter(supported_options)

    @pytest.fixture()
    def valid_inputs(self):
        yield ("1", "42", "99", "100", "-42")

    @pytest.fixture()
    def invalid_inputs(self):
        yield ("1.0", "Five")

    def test_initialiser(self):
        with pytest.raises(TypeError):
            IntegerInputGetter(("42"),)

    def test_is_valid(self, any_integer_input_getter, valid_inputs, invalid_inputs):
        assert all(any_integer_input_getter.is_valid(x) for x in valid_inputs)
        assert not any(any_integer_input_getter.is_valid(x) for x in invalid_inputs)

    def test_parse(self, any_integer_input_getter, valid_inputs):
        expected_outputs = (1, 42, 99, 100, -42)
        observed_outputs = tuple(any_integer_input_getter.parse(x) for x in valid_inputs)

        assert expected_outputs == observed_outputs

    def is_supported(
        self,
        any_integer_input_getter,
        specified_integer_input_getter,
        supported_options,
        unsupported_options
    ):

        assert all(any_integer_input_getter.is_supported(x) for x in supported_options)
        assert all(any_integer_input_getter.is_supported(x) for x in unsupported_options)

        assert all(specified_integer_input_getter.is_supported(x) for x in supported_options)
        assert not any(specified_integer_input_getter.is_supported(x) for x in unsupported_options)

    def test_get_input(self, any_integer_input_getter, specified_integer_input_getter, monkeypatch):
        monkeypatch.setattr('builtins.input', lambda _: "42")

        for getter in (any_integer_input_getter, specified_integer_input_getter):
            assert getter.get_input() == 42

    def test_get_multiple_inputs(
        self,
        any_integer_input_getter,
        specified_integer_input_getter,
        monkeypatch
    ):

        monkeypatch.setattr('builtins.input', lambda _: "42, 100")

        for getter in (any_integer_input_getter, specified_integer_input_getter):
            assert getter.get_multiple_inputs() == (42, 100)


class TestCaseInsensitiveStringInputGetter:
    @pytest.fixture()
    def any_case_insensitive_string_input_getter(self):
        yield CaseInsensitiveStringInputGetter()

    @pytest.fixture()
    def supported_options(self):
        yield ("foo", "bar", "BAZ")

    @pytest.fixture()
    def specified_case_insensitive_string_input_getter(self, supported_options):
        yield CaseInsensitiveStringInputGetter(supported_options)

    @pytest.fixture()
    def inputs(self):
        yield ("foo", "bar", "car", "draw")

    def test_is_valid(self, any_case_insensitive_string_input_getter, inputs):
        assert all(any_case_insensitive_string_input_getter.is_valid(x) for x in inputs)

    def test_parse(
        self,
        any_case_insensitive_string_input_getter,
        specified_case_insensitive_string_input_getter
    ):

        assert any_case_insensitive_string_input_getter.parse("AbC") == "AbC"
        assert any_case_insensitive_string_input_getter.parse("ABC") == "ABC"
        assert any_case_insensitive_string_input_getter.parse("42.0") == "42.0"

        assert specified_case_insensitive_string_input_getter.parse("FoO") == "foo"
        assert specified_case_insensitive_string_input_getter.parse("BAR") == "bar"
        assert specified_case_insensitive_string_input_getter.parse("baz") == "BAZ"
        assert specified_case_insensitive_string_input_getter.parse("BAZ") == "BAZ"

    def test_get_input(
        self,
        any_case_insensitive_string_input_getter,
        specified_case_insensitive_string_input_getter,
        monkeypatch
    ):

        monkeypatch.setattr('builtins.input', lambda _: "FOO")

        assert any_case_insensitive_string_input_getter.get_input() == "FOO"
        assert specified_case_insensitive_string_input_getter.get_input() == "foo"

    def test_get_multiple_inputs(
        self,
        any_case_insensitive_string_input_getter,
        specified_case_insensitive_string_input_getter,
        monkeypatch
    ):

        monkeypatch.setattr('builtins.input', lambda _: "fOo, fOO, BAR")

        assert any_case_insensitive_string_input_getter.get_multiple_inputs() == (
            "fOo", "fOO", "BAR"
        )
        assert specified_case_insensitive_string_input_getter.get_multiple_inputs() == (
            "foo", "foo", "bar"
        )


class TestDateInputGetter:
    @pytest.fixture()
    def supported_options(self):
        yield (dt.date(2022, 1, 1), dt.date(2022, 2, 2), dt.date(2022, 3, 3))

    @pytest.fixture()
    def date_input_getter(self, supported_options):
        yield DateInputGetter(supported_options)

    @pytest.fixture()
    def valid_inputs(self, supported_options):
        yield (
            supported_options[0].strftime("%Y-%m-%d"),
            supported_options[0].strftime("%Y/%m/%d"),
            supported_options[0].strftime("%Y%m%d"),
            supported_options[0].strftime("%d-%m-%Y"),
            supported_options[1].strftime("%d-%m-%Y"),
            supported_options[2].strftime("%d-%m-%Y"),
            supported_options[0].strftime("%d-%m"),
            supported_options[1].strftime("%d-%m"),
            supported_options[2].strftime("%d-%m"),
            str(supported_options[0].day),
            supported_options[1].strftime("%A"),
            supported_options[2].strftime("%A")[:3],
        )

    @pytest.fixture()
    def invalid_inputs(self):
        yield (
            "2022-04-01",
            "Fri",
            "February"
        )

    def test_initialiser(self):
        with pytest.raises(TypeError):
            DateInputGetter(("2022-01-01",))

        with pytest.raises(ValueError):
            DateInputGetter(tuple())

    def test_is_valid(self, date_input_getter, valid_inputs, invalid_inputs):
        assert all(date_input_getter.is_valid(x) for x in valid_inputs)
        assert not any(date_input_getter.is_valid(x) for x in invalid_inputs)

    def test_parse(self, date_input_getter, valid_inputs, supported_options):
        expected_outputs = (
            supported_options[0],
            supported_options[0],
            supported_options[0],
            supported_options[0],
            supported_options[1],
            supported_options[2],
            supported_options[0],
            supported_options[1],
            supported_options[2],
            supported_options[0],
            supported_options[1],
            supported_options[2],
        )
        observed_outputs = tuple(date_input_getter.parse(x) for x in valid_inputs)

        assert observed_outputs == expected_outputs

    def test_get_input(self, date_input_getter, supported_options, monkeypatch):
        monkeypatch.setattr('builtins.input', lambda _: supported_options[0].strftime("%Y%d%m"))
        assert date_input_getter.get_input() == supported_options[0]

    def test_get_multiple_inputs(self, date_input_getter, supported_options, monkeypatch):
        monkeypatch.setattr(
            'builtins.input',
            lambda _: (
                f"{supported_options[0].strftime('%A')[:3]}, "
                f"{supported_options[1].strftime('%A')[:3]}"
            )
        )

        assert date_input_getter.get_multiple_inputs() == (
            supported_options[0],
            supported_options[1]
        )
