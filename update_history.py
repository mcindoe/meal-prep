import datetime as dt

from utils import filter_history
from utils import load_history
from utils import print_history
from utils import delete_history_entries
from utils import DAYS


def get_date_from_weekday(weekday, dates):
    weekday = weekday.strip().lower()
    date_matches = [
        date
        for date in dates
        if DAYS[date.weekday()].lower().startswith(weekday)
    ]
    if not date_matches:
        return None
    return date_matches[0]


def delete_from_last_week():
    today = dt.date.today()
    window_start = today - dt.timedelta(days=7)
    window_end = today + dt.timedelta(days=1)

    print('window start: ', window_start)
    print('window end: ', window_end)
    
    history = load_history()
    
    print(history)

    week_history = filter_history(history, window_start, window_end)

    print('week history: ', week_history)
    
    print()
    print_history(week_history)
    
    while True:
        user_input = input('\nEnter the days of the week to be deleted, separate by commas. C to cancel:\n')
        split_user_input = user_input.split(',')
        if len(split_user_input) == 1 and split_user_input[0].lower() == 'c':
            return

        else:
            user_dates = [
                get_date_from_weekday(
                    day, 
                    dates=list(week_history.keys())
                )
                for day in split_user_input
            ]
            if any([date is None for date in user_dates]):
                print('Unrecognised input')
            else:
                delete_history_entries(user_dates)
                print('\nDeleted the following entries:\n')

                deleted_history = {
                    date: meal
                    for date, meal in week_history.items()
                    if date in user_dates
                }
                print_history(deleted_history)
                print()

                return

if __name__ == '__main__':
    delete_from_last_week()

