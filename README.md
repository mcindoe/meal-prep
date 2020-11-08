# Meal Prep

Automate family meal selection.

Meals are loaded from the meals.json file, and a random selection of meals is suggested for the days specified in recommend.py, according to various rules. The rules are defined in the rules.py file, the docstring there explains what is meant by a rule in this context. A rule might be for example to not recommend the same protein choice on consecutive days, or no two pasta dishes in a week. Rules also incorporate knowledge of history to inform meal selection.

## Future Rules

* Some categories for time required to prepare a meal
	- Provides option to add rules based on number of time-intensive meals to allow in a week

## Future Work

* Ingredients
    - Populate JSON with required ingredients
    - Once selection has been made, form a combined, sorted (by category, name) shopping list with option to ammend based on already-owned items
    - Option to email user with shopping list 
* Email users with a PDF of the meal selection for that week
	- This is tricky with a public repo. Might need to set up a web server to accept requests to interact with email
    - Could include a PDF of the recipe in the email as well
    - Meals could have an optimal recipe parameter (would have stored elsewhere from the JSON), and then if present the email would contain the recipes in order

## Email Support

Currently email support is being provided locally, loading a credentials file at runtime. This file is ignored from the git since it contains password information for the mail robot.

At present if you want email support you must create an email robot and follow e.g. the information [here](https://realpython.com/python-send-email/) to allow for automated sending of emails from this address. You can also disable the email support in the script if this feature isn't required. 

In the future, the solution is to have the script send a request to a web server which emails back the weekly recommendation and shopping list.
