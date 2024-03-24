import os
import unittest

from mealprep.loc import DATA_DIR, ROOT_DIR
from mealprep.meal import PROJECT_DIARY_FILENAME


class TestLoc(unittest.TestCase):
    def test_loc(self):
        self.assertTrue(ROOT_DIR.exists())
        self.assertTrue(DATA_DIR.exists())
        self.assertTrue(PROJECT_DIARY_FILENAME in os.listdir(DATA_DIR))
