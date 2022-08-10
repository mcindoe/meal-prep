"""
Unit tests for the Config class
"""

from mealprep.src.config import config


def test_config():
    """
    Unit tests for the Config class
    """

    assert isinstance(config.email_addresses, list)
    assert len(config.email_addresses) > 0
