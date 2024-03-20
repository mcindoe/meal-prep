import unittest

from mealprep.config import config
from mealprep.constants import ConfigEntries


class TestConfig(unittest.TestCase):
    def test_config(self):
        for entry_name in ConfigEntries.values():
            entry_value = getattr(config, entry_name)

            self.assertTrue(isinstance(entry_value, tuple))
            self.assertGreater(len(entry_value), 0)
