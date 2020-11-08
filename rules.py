'''
Provides the available rules on which to limit the
meals which can be selected for a given date

A meal dictionary is a dictionary name: meal_info
as  found in the meals JSON file. meal_info contains
metadata on the meal.

A rule is a filtering of a meal dictionary, which
accepts and returns a meal dictionary. We also provide
a suitable history and any current recommendations
which is expected to be of interest to all rules. An
example is so that we know what meal was suggested
yesterday and don't want to suggest that meal today.

We ensure that rules have a common interface. To
accomplish this, we provide all information which
may be relevant to each rule. We require rules to
take the form

rule(meals, date, combined_history)

where meals is the meals dictionary, date is the date
on which a meal choice is being made, and combined_history
is a dictionary which contains some suitably long recent
history of meals, as well as any recommendations for the
current week which may in general be before or after
the current date. From the purpose of filtering, these
histories are indistinguishable. Rules must be implemented
in a forward- and backward-looking fashion. E.g. ensure
that we don't suggest a meal today which is suggested
tomorrow already in the combined_history.
'''


import datetime as dt

from utils import filter_history
from utils import get_protein
from utils import is_favourite
from utils import is_fish
from utils import is_pasta
from utils import is_roast


def not_consecutive_same_protein(meals, date, combined_history):
    "Do not recommend the same protein two days in a row"
    previous_day = date - dt.timedelta(days=1)
    next_day = date + dt.timedelta(days=1)

    proteins_to_avoid = []
    if previous_day in combined_history:
        proteins_to_avoid.append(combined_history[previous_day])
    if next_day in combined_history:
        proteins_to_avoid.append(combined_history[next_day])

    return {
        name: meal_info
        for name, meal_info in meals.items()
        if meal_info['protein'] not in proteins_to_avoid
    }


def not_within_seven_days(meals, date, combined_history):
    "Do not recommend the same meal within seven days of previous occurrence"
    window_start = date - dt.timedelta(days=7)
    window_end = date + dt.timedelta(days=8)
    window_history = filter_history(combined_history, window_start, window_end)

    return {
        name: meal_info
        for name, meal_info in meals.items()
        if name not in window_history.values()
    }


def not_non_favourite_within_fourteen_days(meals, date, combined_history):
    "Do not recommend any non-favourite meal within fourteen days of previous occurrence"
    window_start = date - dt.timedelta(days=14)
    window_end = date + dt.timedelta(days=15)
    window_history = filter_history(combined_history, window_start, window_end)

    return {
        name: meal_info
        for name, meal_info in meals.items()
        if is_favourite(name) or name not in window_history.values() 
    }


def not_pasta_within_five_days(meals, date, combined_history):
    "Do not recommend pasta dishes within five days of previous occurrence"
    window_start = date - dt.timedelta(days=5)
    window_end = date + dt.timedelta(days=6)
    window_history = filter_history(combined_history, window_start, window_end)

    if any([is_pasta(meal) for meal in window_history.values()]):
        return {
            name: meal_info
            for name, meal_info in meals.items()
            if not is_pasta(name)
        }

    return meals


def force_sunday_roast(meals, date, combined_history):
    "Recommend only roasts on a Sunday"
    if date.weekday() != 6:
        return meals

    return {
        name: meal_info
        for name, meal_info in meals.items()
        if is_roast(name)
    }


def not_roast_on_non_sunday(meals, date, combined_history):
    "If not on Sunday, do not recommend a roast"
    if date.weekday() == 6:
        return meals

    return {
        name: meal_info
        for name, meal_info in meals.items()
        if not is_roast(name)
    }


def not_fish_within_seven_days(meals, date, combined_history):
    "Do not recommend fish dishes within seven days of previous occurrence"
    window_start = date - dt.timedelta(days=7)
    window_end = date + dt.timedelta(days=8)
    window_history = filter_history(combined_history, window_start, window_end)

    if any([is_fish(meal) for meal in window_history.values()]):
        return {
            name: meal_info
            for name, meal_info in meals.items()
            if not is_fish(name)
        }

    return meals
