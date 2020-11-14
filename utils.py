import datetime as dt
import json
import random
import pickle


HISTORY_FILE = 'history.pkl'
INGREDIENTS_FILE = 'ingredients.json'
MEALS_FILE = 'meals.json'
MAIL_CREDENTIALS_FILE = 'mail_credentials.txt'

DAYS = [
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday',
    'Saturday',
    'Sunday'
]


def get_mail_credentials():
    "Get username, password used by mail robot"
    with open(MAIL_CREDENTIALS_FILE, 'r') as fp:
        lines = fp.readlines()
    username, password = (line.rstrip('\n') for line in lines)
    return username, password


def load_meals():
    with open(MEALS_FILE, 'r') as fp:
        meals = json.load(fp)
    return meals


def write_meals(meals):
    # TODO: check that meals are compliant, e.g. all ingredients supported,
    # before writing to file
    with open(MEALS_FILE, 'w') as fp:
        json.dump(meals, fp, indent=4)


def load_ingredients():
    with open(INGREDIENTS_FILE, 'r') as fp:
        ingredients = json.load(fp)
    return ingredients


def write_ingredients(ingredients):
    with open(INGREDIENTS_FILE, 'w') as fp:
        json.dump(ingredients, fp, indent=4)


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
    meals = load_meals()
    for history_meal in history.values():
        if history_meal not in meals.keys():
            print(f"Cannot write {history_meal} to history since it is not a supported meal")
            return

    with open(HISTORY_FILE, 'wb') as fp:
        pickle.dump(history, fp)


def write_history_entry(date, entry):
    meals = load_meals()
    if entry not in meals.keys():
        print(f"Cannot write {entry} to history since it is not a supported meal")
        return

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


def delete_history_window(start_date, end_date):
    "start_date, end_date: dt.date. End not included"

    history = load_history()
    history = {
        d: entry
        for d, entry in history.items()
        if d < start_date or d >= end_date
    }
    write_history(history)


def choose_meal(meals):
    return random.choice(list(meals.keys()))


def print_history(history):
    sorted_dates = sorted(list(history.keys()))
    day_names = [DAYS[date.weekday()] for date in sorted_dates]
    longest_day_len = max([len(day) for day in day_names])

    for date, day in zip(sorted_dates, day_names):
        recommended_meal = history[date]
        print("{0: <{1}} - {2}".format(day, longest_day_len, recommended_meal))


def display_recommendation(rec):
    print('\nRecommendation for this week:\n')
    print_history(rec)
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

    if 'protein' not in meals[meal_name].keys():
        return None
    return meals[meal_name]['protein']


def is_fish(meal_name):
    meals = load_meals()
    assert meal_name in meals.keys()

    if 'protein' not in meals[meal_name]:
        return False
    return meals[meal_name]['protein'] == 'fish'


def is_attr(attr):
    def f(meal_name):
        meals = load_meals()
        assert meal_name in meals.keys()

        if attr not in meals[meal_name]:
            return False
        return meals[meal_name][attr]
    
    return f


is_pasta = is_attr('pasta')
is_roast = is_attr('roast')
is_favourite = is_attr('favourite')
is_difficult = is_attr('difficult')

