from mealprep.src.config import Config


def test_config():
    config = Config()

    assert isinstance(config.get_email_addresses(), list)
