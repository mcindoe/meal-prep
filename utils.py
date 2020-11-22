import calendar
import datetime as dt
import json
import random
import pickle

import meal

EXTRAS_FILE = 'data/extras.json'
HISTORY_FILE = 'data/history.json'
INGREDIENTS_FILE = 'data/ingredients.json'
MEALS_FILE = 'data/meals.json'
MAIL_CREDENTIALS_FILE = 'mail_credentials.txt'

JSON_INDENT = 4

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
        json.dump(meals, fp, indent=JSON_INDENT)


def load_ingredients():
    with open(INGREDIENTS_FILE, 'r') as fp:
        ingredients = json.load(fp)
    return ingredients


def write_ingredients(ingredients):
    with open(INGREDIENTS_FILE, 'w') as fp:
        json.dump(ingredients, fp, indent=JSON_INDENT)


def load_extras():
    with open(EXTRAS_FILE, 'r') as fp:
        extras = json.load(fp)
    return extras


def load_vegetables():
    extras = load_extras()
    return extras['vegetables']


def load_sides():
    extras = load_extras()
    return extras['sides']


def load_additionals():
    extras = load_extras()
    return extras['additionals']


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
    Reads the history JSON file and converts
    to a dictionary keyed by dt.dates, valued
    by meal.Meals. Optional filtering to 
    dates in start <= date < end.

    start: dt.datetime
    end: dt.datetime
    '''
    
    with open(HISTORY_FILE, 'r') as fp:
        json_history = json.load(fp)

    history = {}
    for date_str, meal_info in json_history.items():
        year, month, day = [int(el) for el in date_str.split('/')]
        date = dt.date(year, month, day)
        
        history[date] = meal.Meal.from_json(meal_info)

    return filter_history(history, start, end)


def write_history(history):
    '''
    Write history dictionary information to file,
    in a JSON format.

    history (dict: key=dt.date, val=meal.Meal)
    '''

    meals = load_meals()

    json_history = {}
    for date, meal in history.items():
        if meal.name not in meals.keys():
            print(f"Cannot write {meal.name} to history - not a supported meal")
            return

        date_str = date.strftime('%Y/%m/%d')
        json_history[date_str] = meal.to_json()

    sorted_keys = sorted(json_history.keys())
    sorted_history = {
        date_str: json_history[date_str]
        for date_str in sorted_keys
    }

    with open(HISTORY_FILE, 'w') as fp:
        json.dump(sorted_history, fp, indent=JSON_INDENT)


def write_history_entry(date, meal):
    meals = load_meals()
    if meal.name not in meals.keys():
        print(f"Cannot write {meal.name} to history - not a supported meal")
        return

    history = load_history()
    history[date] = meal
    write_history(history)


def write_history_entries(entries):
    '''entries: dictionary of dt.date: meal.Meal'''
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


def get_history_meal_names(history):
    return [meal.name for meal in history.values()]


def get_close_history(history, pivot, n_days):
    start = pivot - dt.timedelta(days=n_days)
    end = pivot + dt.timedelta(days=n_days+1)
    return filter_history(history, start, end)


def get_close_history_meal_names(history, pivot, n_days):
    close_history = get_close_history(history, pivot, n_days)
    return get_history_meal_names(close_history)


def get_vegetables(meal):
    meals = load_meals()

    if 'vegetables' not in meals[meal].keys():
        return None
    return meals[meal]['vegetables']


def choose_meal(meals):
    '''
    From the passed dict of meals, choose a meal
    and make any additional choices (e.g. veg)
    about the meal. Return a Meal instance
    '''
    name = random.choice(list(meals.keys()))
    vegetables = get_vegetables(name)
    if vegetables is None:
        return meal.Meal(name)
    veg_choice = random.choice(vegetables)
    
    return meal.Meal(name, [veg_choice])


def make_date_string(date):
    '''Return a string of dt.date in the form Sun, 22nd of Nov'''
    day_str = calendar.day_name[date.weekday()][:3]
    month_str = calendar.month_name[date.month][:3]
    final_day_num = int(str(date.day)[-1])
    
    if final_day_num == 1:
        day_suffix = 'st'
    elif final_day_num == 2:
        day_suffix = 'nd'
    elif final_day_num == 3:
        day_suffix = 'rd'
    else:
        day_suffix = 'th'

    return f'{day_str}, {date.day}{day_suffix} of {month_str}'


def print_history(history=load_history(), with_index=False):
    sorted_dates = sorted(list(history.keys()))
    date_strings = [make_date_string(date) for date in sorted_dates]
    longest_date_str_len = max([len(date_str) for date_str in date_strings])

    if with_index:
        largest_index_len = len(str(len(history)+1))

    for idx, (date, date_str) in enumerate(zip(sorted_dates, date_strings)):
        recommended_meal = history[date]
        if with_index:
            print("{0: <{1}} {2: <{3}} - {4}".format(idx+1, largest_index_len, date_str, longest_date_str_len, recommended_meal))
        else:
            print("{0: <{1}} - {2}".format(date_str, longest_date_str_len, recommended_meal))


def display_recommendation(rec, with_index=False):
    print('\nRecommendations:\n')
    print_history(rec, with_index)
    print()


def get_protein(meal_name):
    meals = load_meals()
    assert meal_name in meals.keys(), f'Unsupported meal {meal_name}'

    if 'protein' not in meals[meal_name].keys():
        return None
    return meals[meal_name]['protein']


def is_fish(meal):
    return get_protein(meal) == 'fish'


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
is_time_consuming = is_attr('time-consuming')


def make_list_str(elements):
    '''
    Format a list into a string, separating items
    by commas and a final " and "
    '''
    if elements is None:
        return ''

    if len(elements) == 1:
        return str(elements[0])

    first_elements = elements[:-1]
    last_element = elements[-1]
    return f'{", ".join(first_elements)} and {last_element}'


def match_month(month_str):
    month_matches = [
        month
        for month in list(calendar.month_names)
        if month.upper().startswith(month_str.upper())
    ]
    if not month_matches:
        return None
    return month_matches[0] 

