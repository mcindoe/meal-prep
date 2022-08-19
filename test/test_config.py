from mealprep.src.config import config
from mealprep.src.constants import ConfigEntries

def test_config():
    for entry_name in ConfigEntries.values():
        entry_value = getattr(config, entry_name)

        assert isinstance(entry_value, tuple)
        assert len(entry_value) > 0
