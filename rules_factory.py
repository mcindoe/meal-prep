'''
Factory function for rules. If we need a specific rule, but
cannot naturally be expressed with the usual rule interface,
can use this factory to generate a rule with the required
interface.
'''

def dated_avoid_meal(avoid_date, avoided_meal):
    def dated_avoid_meal_rule(meals, date, combined_history):
        if date != avoid_date:
            return meals

        return {
            meal: meal_info
            for meal, meal_info in meals.items()
            if meal != avoided_meal
        }

    return dated_avoid_meal_rule


def avoid_meal(avoided_meal):
    def avoid_meal_rule(meals, date, combined_history):
        return {
            meal: meal_info
            for meal, meal_info in meals.items()
            if meal != avoided_meal
        }
        
    return avoid_meal_rule
