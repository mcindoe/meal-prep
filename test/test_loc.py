import os

from mealprep.src.loc import ROOT_DIR
from mealprep.src.loc import DATA_DIR
from mealprep.src.meal import PROJECT_DIARY_FILENAME


def test_loc():
	assert ROOT_DIR.exists()
	assert PROJECT_DIARY_FILENAME in os.listdir(DATA_DIR)