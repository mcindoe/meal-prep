import datetime as dt
import unittest

from mealprep.utils import get_day_suffix, get_pretty_print_date_string


class TestUtils(unittest.TestCase):
    def test_get_day_suffix(self):
        with self.assertRaises(TypeError):
            get_day_suffix("42")

        self.assertEqual(get_day_suffix(8), "th")
        self.assertEqual(get_day_suffix(9), "th")
        self.assertEqual(get_day_suffix(10), "th")
        self.assertEqual(get_day_suffix(11), "th")
        self.assertEqual(get_day_suffix(20), "th")

        self.assertEqual(get_day_suffix(1), "st")
        self.assertEqual(get_day_suffix(2), "nd")
        self.assertEqual(get_day_suffix(3), "rd")

        self.assertEqual(get_day_suffix(31), "st")

    def test_get_pretty_print_date_string(self):
        self.assertEqual(
            get_pretty_print_date_string(dt.date(2022, 1, 5), include_year=True), "Wed 5th Jan 2022"
        )
        self.assertEqual(get_pretty_print_date_string(dt.date(2022, 1, 5)), "Wed 5th Jan")
        self.assertEqual(
            get_pretty_print_date_string(dt.date(2022, 1, 5), include_date_number_spacing=True),
            "Wed  5th Jan",
        )
