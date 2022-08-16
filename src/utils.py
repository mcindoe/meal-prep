import itertools


def get_day_suffix(day_number: int) -> str:
    """
    Get the suffix portion of a date from the date number, e.g.
    2 -> 'nd', 13 -> 'th'
    """

    assert isinstance(day_number, int), "get_day_suffix must be passed an integer"

    if day_number in itertools.chain(range(4, 21), range(24, 31)):
        return "th"
    return ("st", "nd", "rd")[day_number % 10 - 1]
