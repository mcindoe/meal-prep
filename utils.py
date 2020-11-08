import datetime as dt
import json
import random
import pickle


MEALS_FILE = 'meals.json'
HISTORY_FILE = 'history.pkl'

DAYS = [
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday',
    'Saturday',
    'Sunday'
]


def load_meals():
    with open(MEALS_FILE, 'r') as fp:
        meals = json.load(fp)
    return meals


def filter_history(history, start=None, end=None):
    if start is not None:
        history = {
            date: entry
            for date, entry in history.items()
            if date >= start
        }

    if end is not None:
        history = {
            date: entry
            for date, entry in history.items()
            if date < end
        }

    return history


def load_history(start=None, end=None):
    '''
    start: dt.datetime
    end: dt.datetime
    '''

    with open(HISTORY_FILE, 'rb') as fp:
        history = pickle.load(fp)

    return filter_history(history, start, end)


def write_history(history):
    with open(HISTORY_FILE, 'wb') as fp:
        pickle.dump(history, fp)


def write_history_entry(date, entry):
    history = load_history()
    history[date] = entry
    write_history(history)


def write_history_entries(entries):
    '''entries: dictionary of date: choice'''
    history = load_history()

    sorted_dates = sorted(list(entries.keys()))
    for date in sorted_dates:
        history[date] = entries[date]
    write_history(history)


def delete_history_entries(dates):
    '''
    dates: dt.date or iterable of dt.dates
    '''
    if isinstance(dates, dt.date):
        dates = [dates]

    history = load_history()
    history = {
        d: entry
        for d, entry in history.items()
        if d not in dates
    }
    write_history(history)


def choose_meal(meals):
    return random.choice(list(meals.keys()))


def display_recommendation(rec):
    sorted_dates = sorted(rec.keys())
    day_names = [DAYS[date.weekday()] for date in sorted_dates]
    longest_day_len = max([len(day) for day in day_names])

    print('\nRecommendation for this week:\n')
    for date, day in zip(sorted_dates, day_names):
        recommended_meal = rec[date]
        print("{0: <{1}} - {2}".format(day, longest_day_len, recommended_meal))
    print()


def find_day(day_str):
    '''
    Find the day of the week from a user-input string.
    Expected to be the start of the string.
    '''

    day_str = day_str.strip().lower()
    matching_days = [
        day
        for day in DAYS
        if day.lower().startswith(day_str)
    ]
    if not matching_days:
        return None
    return matching_days[0]


def get_protein(meal_name):
    meals = load_meals()
    assert meal_name in meals.keys()
    return meals[meal_name]['protein']


def is_pasta(meal_name):
    meals = load_meals()
    assert meal_name in meals.keys()

    if 'pasta' not in meals[meal_name]:
        return False
    return meals[meal_name]['pasta']


def is_roast(meal_name):
    meals = load_meals()
    assert meal_name in meals.keys()

    if 'roast' not in meals[meal_name]:
        return False
    return meals[meal_name]['roast']
