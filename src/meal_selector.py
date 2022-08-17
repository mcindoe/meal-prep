import datetime as dt
import random
from typing import Iterable

from mealprep.src.exceptions import OutOfMealsError
from mealprep.src.meal import MealCollection
from mealprep.src.meal import MealDiary
from mealprep.src.rule import RuleCollection
from mealprep.src.user_input_getter import CaseInsensitiveStringInputGetter
from mealprep.src.user_input_getter import DateInputGetter


class MealSelector:
    def __init__(
        self,
        meal_collection: MealCollection,
        rule_collection: RuleCollection,
        original_meal_diary: MealDiary
    ):

        self.meal_collection = meal_collection.copy()
        self.rule_collection = rule_collection.copy()
        self.original_meal_diary = original_meal_diary.copy()

    def recommend(self, dates: Iterable[dt.date], recommended_diary: MealDiary = None) -> MealDiary:
        """
        Recommend a MealDiary of Meals for the specified dates

        The returned diary is built by choosing randomly from the subset
        of supported meals which maximise the number of choices for the
        next date

        The recommended_diary is a current, proposed addition to the
        meal diary, as opposed to the original_meal_diary which exists
        outside of this selector
        """

        # TODO: Consider sorted(dates). Check that this works with genexprs
        dates = sorted(x for x in dates)

        if recommended_diary is None:
            meal_diary = self.original_meal_diary.copy()
        else:
            meal_diary = self.original_meal_diary.upsert(recommended_diary)

        # Check that dates does not contain any duplicates
        if len(dates) != len(set(dates)):
            raise ValueError("Passed dates contains duplicate elements")

        # Check that none of the passed dates are in the meal diary
        if set(dates).intersection(meal_diary.dates):
            raise ValueError("Some passed dates are already in the meal diary")

        for idx, date in enumerate(dates):
            meal_choices = self.rule_collection(self.meal_collection, date, meal_diary)

            if not meal_choices:
                raise OutOfMealsError(f"Ran out of meals on date {date.strftime(MealDiary.DATE_FORMAT)}")

            if date == dates[-1]:
                meal_diary[date] = random.choice(meal_choices.meals)
                break

            # Compute, for each meal, if that were the chosen meal, how many meals would be
            # available to choose from next date
            available_meals_for_next_date = {}
            for meal in meal_choices.meals:
                proposed_diary = meal_diary.copy()
                proposed_diary[date] = meal

                next_date = dates[idx+1]

                next_date_meal_choices = self.rule_collection(
                    self.meal_collection,
                    next_date,
                    proposed_diary
                )

                available_meals_for_next_date[meal] = len(next_date_meal_choices)

            # Compute the subcollection of meals which maximise the number of available
            # choices for the next date
            largest_number_of_choices = max(available_meals_for_next_date.values())
            meals_leaving_most_choice = [
                meal
                for meal in meal_choices.meals
                if available_meals_for_next_date[meal] == largest_number_of_choices
            ]

            meal_diary[date] = random.choice(meals_leaving_most_choice)

        # Return only the new, recommended portion of the diary
        return meal_diary.difference(self.original_meal_diary)

    def recommend_until_confirmed(self, dates: Iterable[dt.date]) -> MealDiary:
        user_confirmed_getter = CaseInsensitiveStringInputGetter(("Y", "N"))
        recommended_diary = None

        while True:
            if recommended_diary:
                dates_to_compute_recommendations_for = set(dates) - set(recommended_diary.dates)
            else:
                dates_to_compute_recommendations_for = dates

            recommended_diary = self.recommend(dates_to_compute_recommendations_for, recommended_diary)

            print("Recommended meal plan:")
            print(recommended_diary.get_pretty_print_string())

            print("Sound okay? Enter 'Y' or 'N'")
            if user_confirmed_getter.get_input() == "Y":
                return recommended_diary

            user_changed_dates_input_getter = DateInputGetter(dates)

            print("Enter dates to change")
            dates_to_change = set(user_changed_dates_input_getter.get_multiple_inputs())
            recommended_diary = recommended_diary.except_dates(changed_dates)

        # Return only the new, recommended portion of the diary
        return recommended_diary.difference(self.original_meal_diary)
