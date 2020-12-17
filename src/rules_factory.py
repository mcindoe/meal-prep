"""
Factory functions for rules. If we need a specific rule, but
it cannot naturally be expressed with the usual rule interface,
can use this factory to generate a rule with the required
interface.
"""

import datetime as dt


def dated_avoid_meal(avoid_date: dt.date, avoided_meal: str):
    """
    Do not recommend the avoided meal on the avoided date
    """

    def dated_avoid_meal_rule(meals, date, combined_history):
        if date != avoid_date:
            return meals

        return {
            meal: meal_info
            for meal, meal_info in meals.items()
            if meal != avoided_meal
        }

    return dated_avoid_meal_rule


def avoid_meal(avoided_meal: str):
    """
    Do not recommend the meal
    """

    def avoid_meal_rule(meals, date, combined_history):
        return {
            meal: meal_info
            for meal, meal_info in meals.items()
            if meal != avoided_meal
        }

    return avoid_meal_rule
