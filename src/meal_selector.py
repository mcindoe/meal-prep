import datetime as dt
import random
from typing import Iterable
from typing import Optional
from typing import Union

from mealprep.src.exceptions import OutOfMealsError
from mealprep.src.meal import MealCollection
from mealprep.src.meal import MealDiary
from mealprep.src.rule import RuleCollection
from mealprep.src.rule import NotSpecifiedMealOnSpecifiedDate
from mealprep.src.user_input_getter import CaseInsensitiveStringInputGetter
from mealprep.src.user_input_getter import DateInputGetter


class MealSelector:
    def __init__(
        self,
        meal_collection: MealCollection,
        rule_collection: RuleCollection,
        meal_diary: MealDiary
    ):

        if not isinstance(meal_collection, MealCollection):
            raise TypeError("'meal_collection' argument must be a MealCollection")

        if not isinstance(rule_collection, RuleCollection):
            raise TypeError("'rule_collection' argument must be a RuleCollection")

        if not isinstance(meal_diary, MealDiary):
            raise TypeError("'meal_diary' argument must be a MealDiary")

        self.meal_collection = meal_collection.copy()
        self.original_rule_collection = rule_collection.copy()
        self.original_meal_diary = meal_diary.copy()

    def recommend(
        self,
        dates: Iterable[dt.date],
        rule_collection: RuleCollection,
        recommended_diary: Optional[MealDiary] = None
    ) -> MealDiary:
        """
        Recommend a MealDiary of Meals for the specified dates

        The returned diary is built by choosing randomly from the subset
        of supported meals which maximise the number of choices for the
        next date

        The rule_collection is the current set of rules to apply to
        MealCollections on specified dates

        The recommended_diary is a current, proposed addition to the
        meal diary, as opposed to the original_meal_diary which exists
        outside of this selector
        """

        dates = sorted(dates)

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
            meal_choices = rule_collection(self.meal_collection, date, meal_diary)

            if not meal_choices:
                raise OutOfMealsError(f"Ran out of meals on date {date.strftime(MealDiary.DATE_FORMAT)}")

            # If there is no next date to consider, choose randomly from acceptable meals
            if date == dates[-1]:
                meal_diary[date] = random.choice(meal_choices)
                break

            # Otherwise, if there is a next date, choose randomly from meals which leave as
            # much choise as possible for the next date
            n_available_meals_for_next_date = {}
            for meal in meal_choices:
                proposed_diary = meal_diary.copy()
                proposed_diary[date] = meal

                next_date = dates[idx+1]

                next_date_meal_choices = rule_collection(
                    self.meal_collection,
                    next_date,
                    proposed_diary
                )

                n_available_meals_for_next_date[meal] = len(next_date_meal_choices)

            # Compute the subcollection of meals which maximise the
            # number of available choices for the next date
            largest_number_of_choices = max(n_available_meals_for_next_date.values())
            meals_leaving_most_choice = tuple(
                meal
                for meal in meal_choices
                if n_available_meals_for_next_date[meal] == largest_number_of_choices
            )

            meal_diary[date] = random.choice(meals_leaving_most_choice)

        # Return only the new, recommended portion of the diary
        return meal_diary.difference(self.original_meal_diary)

    def recommend_until_confirmed(self, dates: Iterable[dt.date]) -> Union[None, MealDiary]:
        user_confirmed_getter = CaseInsensitiveStringInputGetter(("Y", "N"))
        rule_collection = self.original_rule_collection.copy()
        recommended_diary = None

        while True:
            if recommended_diary:
                dates_to_compute_recommendations_for = set(dates) - set(recommended_diary.dates)
            else:
                dates_to_compute_recommendations_for = dates

            recommended_diary = self.recommend(
                dates_to_compute_recommendations_for,
                rule_collection,
                recommended_diary
            )

            print("\nRecommended meal plan:")
            print(recommended_diary.get_pretty_print_string())

            print("\nSound okay? Enter 'Y' or 'N'")
            user_confirmed_input = user_confirmed_getter.get_input()
            if user_confirmed_input is None:
                return
            if user_confirmed_input == "Y":
                return recommended_diary

            user_changed_dates_input_getter = DateInputGetter(dates)

            print("\nEnter dates to change")
            dates_to_change_input = user_changed_dates_input_getter.get_multiple_inputs()
            if dates_to_change_input is None:
                return
            dates_to_change = set(dates_to_change_input)

            # Don't recommend user-rejected (date, meal) pairs again
            for date in dates_to_change:
                meal_to_avoid = recommended_diary[date]
                avoid_same_suggestion_rule = NotSpecifiedMealOnSpecifiedDate(
                    date,
                    meal_to_avoid
                )
                rule_collection = rule_collection.append(avoid_same_suggestion_rule)

            recommended_diary = recommended_diary.except_dates(dates_to_change)

        # Return only the new, recommended portion of the diary
        return recommended_diary.difference(self.original_meal_diary)
