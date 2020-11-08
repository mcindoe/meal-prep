# Meal Prep

Automate family meal selection.

Meals are loaded from the meals.json file, and a random selection of meals is suggested for the days specified in recommend.py, according to various rules. The rules are defined in the rules.py file, the docstring here explains what is meant by a rule in this context. A rule might be for example not to recommend the same protein choice on consecutive days, or no two pasta dishes consecutively. Rules also incorporate knowledge of history to inform meal selection.

## Future Work

Include ingredients required in meals JSON, allow the generation of a shopping list from the selection recommended. 

