import calendar
import datetime as dt
import random

import rules
import rules_factory
from utils import choose_meal
from utils import display_recommendation
from utils import filter_history
from utils import get_protein
from utils import load_history
from utils import load_meals
from utils import write_history_entries
from utils import match_month


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
        if not available_meals:
            return

        current_rec[date] = choose_meal(available_meals)

    return current_rec


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

        if not current_rec:
            print('Error: No meals match the current filters')
            return

        display_recommendation(current_rec)
        user_input = input('Sound Good? (Y/N/Cancel) ')[0].upper()

        while user_input not in ['Y', 'N', 'C']:
            user_input = input('Please enter Y(es), N(o), or C(ancel) ')[0].upper()

        if user_input == 'Y':
            selection_found = True

        elif user_input == 'N':
            user_index_input_accepted = False
            display_recommendation(current_rec, with_index=True)
            user_index_input = input('Enter the meal indices to change, separated by commas: (C to Cancel)\n')

            while not user_index_input_accepted:
                # break out of loop if user cancels
                if any([el.upper() == 'C' for el in split_user_dates]):
                    return

                split_user_index_input = [el.strip() for el in user_index_input.split(',')]

                inputs_are_integers = True
                for el in split_user_index_input:
                    try:
                        int(el)
                    except ValueError:
                        print("Input not recognised")
                        inputs_are_integers = False
                        break

                if inputs_are_integers:
                    input_indices = {int(el) for el in split_user_index_input}
                    displayed_indices = range(1, len(current_rec)+1)
                    if any([el not in displayed_indices for el in input_indices]):
                        print("Input contains a day which was not recommended")
                    else:
                        user_index_input_accepted = True
                        sorted_recommended_dates = sorted(list(current_rec.keys()))
                        user_dates = [sorted_recommended_dates[idx-1] for idx in input_indices]

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

    write_history_entries(current_rec)
    print('\nBon Appetit! History has been updated\n')


if __name__ == '__main__':
    required_dates = [
        dt.date(2020, 11, 26) + dt.timedelta(days=n)
        for n in range(10)
    ]
    chosen_rules = [
        rules.not_within_seven_days,
        rules.not_non_favourite_within_fourteen_days,
        rules.not_consecutive_same_protein,
        rules.not_pasta_within_five_days,
        rules.not_roast_on_non_sunday,
        rules.force_sunday_roast,
        rules.not_time_consuming_on_weekend,
    ]
    loop_recommend(required_dates, chosen_rules)

