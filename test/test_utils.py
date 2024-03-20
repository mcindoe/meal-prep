import datetime as dt

import pytest

from mealprep.utils import get_day_suffix, get_pretty_print_date_string


def test_get_day_suffix():
    with pytest.raises(TypeError):
        get_day_suffix("42")

    assert get_day_suffix(8) == "th"
    assert get_day_suffix(9) == "th"
    assert get_day_suffix(10) == "th"
    assert get_day_suffix(11) == "th"
    assert get_day_suffix(20) == "th"

    assert get_day_suffix(1) == "st"
    assert get_day_suffix(2) == "nd"
    assert get_day_suffix(3) == "rd"

    assert get_day_suffix(31) == "st"


def test_get_pretty_print_date_string():
    assert (
        get_pretty_print_date_string(dt.date(2022, 1, 5), include_year=True) == "Wed 5th Jan 2022"
    )
    assert get_pretty_print_date_string(dt.date(2022, 1, 5)) == "Wed 5th Jan"
    assert (
        get_pretty_print_date_string(dt.date(2022, 1, 5), include_date_number_spacing=True)
        == "Wed  5th Jan"
    )
