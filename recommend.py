import datetime as dt
import random

import rules
import rules_factory
from utils import filter_history
from utils import get_protein
from utils import load_history
from utils import load_meals
from utils import write_history_entries

DAYS = [
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday',
    'Saturday',
    'Sunday'
]

REQUIRED_DAYS = [
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
]


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


def get_available_meals(date, applied_rules, current_rec):
    '''
    Applies each of the applied_rules successively
    to attain an overall filtering of the full dict
    of available meals. Rules are passed relevant
    history and current meal selection.

    date (dt.date)
    applied_rules (iter of rule functions from rules module)
    current_rec (dict: key=dt.date, val=meal selection)
    '''

    meals = load_meals()
    history = load_history()

    # only pass a generous recent history rather than
    # full history, so this doesn't grow unbounded
    filtered_history = filter_history(
        history,
        start = date - dt.timedelta(days=60)
    )

    combined_history = {**filtered_history, **current_rec}

    for rule in applied_rules:
        meals = rule(meals, date, combined_history)

    return meals


def recommend(dates, applied_rules, current_rec):
    '''
    Suggests meals for the dates specified. Any
    date in dates which is already in current_rec
    remains unchanged.

    dates (iter of dt.date)
    applied_rules (iter of rule functions from rules module)
    current_rec (dict: key=dt.date, val=meal selection)
    '''
    inv_dates = [
        date
        for date in dates
        if date not in current_rec.keys()
    ]

    for date in inv_dates:
        available_meals = get_available_meals(date, applied_rules, current_rec)
        current_rec[date] = choose_meal(available_meals)

    return current_rec


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


def loop_recommend(dates, applied_rules):
    '''
    Make suggestions and prompt user to accept or
    re-suggest certain dates until a suitable
    selection is found. Then write history to file
    '''

    selection_found = False
    current_rec = {}
    while not selection_found:
        current_rec = recommend(dates, applied_rules, current_rec)
        display_recommendation(current_rec)
        user_input = input('Sound Good? (Y/N/Cancel) ')[0].upper()

        while user_input not in ['Y', 'N', 'C']:
            user_input = input('Please enter Y(es), N(o), or C(ancel) ')[0].upper()

        if user_input == 'Y':
            selection_found = True

        elif user_input == 'N':
            user_days_found = False
            while not user_days_found:
                user_day_input = input('Enter the days to change, separated by a comma. (C to Cancel):\n')
                split_user_days = user_day_input.split(',')

                # break out of loop if user cancels
                if any([day.strip().upper() == 'C' for day in split_user_days]):
                    return

                user_days = [find_day(day) for day in split_user_days]
                recommended_days = [DAYS[day.weekday()] for day in current_rec.keys()]
                
                if any([day is None for day in user_days]):
                    print("Input not recognised")
                elif any([day not in recommended_days for day in user_days]):
                    print("Input contains a day which was not recommended")
                else:
                    user_days_found = True

            user_dates = [next_weekday(dt.date.today(), day) for day in user_days]

            # add a rule to not recommend the meals which have been rejected
            for date in user_dates:
                rejected_meal = current_rec[date]
                new_rule = rules_factory.dated_avoid_meal(date, rejected_meal)
                applied_rules.append(new_rule)
            
            current_rec = {
                date: meal_choice
                for date, meal_choice in current_rec.items()
                if date not in user_dates
            }

        elif user_input == 'C':
            return

    # write_history_entries(selection)
    user_email_input = input('\nShould I email you the menu? (Y/N) ').upper()
    print('\nBon Appetit!\n')




def next_weekday(pivot, weekday):
    '''
    Return the dt.date of the next occurrence of weekday
    strictly after pivot

    weekday (str): Entry of DAYS. E.g. "Monday" not "0"
    pivot (dt.date)

    Returns dt.date
    '''
    assert weekday in DAYS
    week_number = DAYS.index(weekday)
    days_ahead = week_number - pivot.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return pivot + dt.timedelta(days=days_ahead)


if __name__ == '__main__':
    required_dates = [
        next_weekday(dt.date.today(), day)
        for day in REQUIRED_DAYS
    ]
    chosen_rules = [
        rules.none_within_seven_days,
        rules.not_consecutive_same_protein,
        rules.not_consecutive_pasta
    ]
    loop_recommend(required_dates, chosen_rules)

