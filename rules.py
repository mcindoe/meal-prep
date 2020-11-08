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
from utils import is_pasta


def not_consecutive_same_protein(meals, date, combined_history):
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


def none_within_seven_days(meals, date, combined_history):
    "Ensure that there is no repeated suggestion within a seven-day window"
    window_start = date - dt.timedelta(days=7)
    window_end = date + dt.timedelta(days=8) 
    window_history = filter_history(combined_history, window_start, window_end)

    return {
        name: meal_info
        for name, meal_info in meals.items()
        if name not in window_history.values()
    }


def not_consecutive_pasta(meals, date, combined_history):
    "Ensure that two pasta dishes are not consecutively recommended"
    window_start = date - dt.timedelta(days=1)
    window_end = date + dt.timedelta(days=2)
    window_history = filter_history(combined_history, window_start, window_end)

    if any([is_pasta(meal) for meal in window_history.values()]):
        return {
            name: meal_info
            for name, meal_info in meals.items()
            if not meal_info['pasta']
        }

    return meals

