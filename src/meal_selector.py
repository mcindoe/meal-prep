import datetime as dt
import random
from typing import Iterable

from mealprep.src.exceptions import OutOfMealsError
from mealprep.src.meal import MealCollection
from mealprep.src.meal import MealDiary
from mealprep.src.rule import RuleCollection
from mealprep.src.user_input_getter import IntegerInputGetter
from mealprep.src.user_input_getter import StringInputGetter


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
                for meal in meal_choices
                if available_meals_for_next_date[meal] == largest_number_of_choices
            ]

            meal_diary[date] = random.choice(meals_leaving_most_choice)

        # Return only the new, recommended portion of the diary
        return meal_diary.difference(self.original_meal_diary)

    def recommend_until_confirmed(self, dates: Iterable[dt.date]) -> MealDiary:
        user_confirmed_getter = StringInputGetter(("Y", "N"))
        recommended_diary = None

        while True:
            recommended_diary = self.recommend(dates, recommended_diary)

            print("Recommended meal plan:")
            print(recommended_diary)

            print("Sound okay? Enter 'Y' or 'N'")
            user_confirmed_input = user_confirmed_getter.get_input()
            if user_confirmed_input is None:
                return

            if user_confirmed_input == "Y":
                return recommended_diary

            # TODO: Have this use e.g. "2nd, 4th" instead of indexes
            user_changed_dates_input_getter = IntegerInputGetter(range(len(dates)))

            print("Date indices")
            for idx, date in enumerate(dates):
                print(f"{idx}\t{date.strftime(MealDiary.DATE_FORMAT)}")

            print("Enter indices of dates to change")
            changed_dates_indices = user_changed_dates_input_getter.get_multiple_inputs()
            changed_dates = set(dates[idx] for idx in changed_dates_indices)
            recommended_diary = MealDiary({
                date: meal
                for date, meal in recommended_diary.items()
                if date not in changed_dates
            })

        # Return only the new, recommended portion of the diary
        return recommended_diary.difference(self.original_meal_diary)
