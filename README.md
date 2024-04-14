# Meal Prep

An application to automate the process of selecting a set of meals to have according to user-defined rules, and
the generation of the corresponding shopping list.

## Usage

Meals are defined by recipes (YAML description of ingredients and addition meal information) found in the`data/recipes`
directory. The supported ingredients are defined in the `ingredients.csv` file. Recipes in the `excluded` recipes
directory will not be suggested to the user.

Meals have associated *properties* and *tags*. A *property* is a key-value pair, and all properties should be provided
for all meals. An example would be `meat=chicken`. A *tag* is a boolean flag which is taken to be True if present, and
False otherwise, for example `Roast` or `Healthy`.

The config file `config.yaml` is used to specify runtime configuration, such as which dates to generate a meal plan for,
and which rules to apply. The rules are specified by the name in the associated enum found in `src/rules.py`.

A `MealDiary` is a mapping from dates to meals. A rule is a filter applied to a meal collection, in the context of a
date and a meal diary. This context is required to apply rules to a collection, for example for the rule "don't
recommend the same meat on consecutive days" we need to know what the date in question is, and what meals have been had
before and after that date (if any).

## Application Launch Files

The project launch files are found in `mealprep/app`. You can run the scripts from the project's root directory by
activating the virtual environment and then running e.g. `python -m mealprep.app.recommend_meals`

`recommend_meals` is the main launch script. Running this module as shown above  will run the application with the
runtime configuration specified in the `config.yaml` file. A selection of meals which don't violate the specified rules
are suggested, and the user is prompted to accept the plan or change meals on specified dates. Once rejected, a
specified (date, meal) pair will not be recommended again. This process is re-run until the user confirms the selection,
or until it is not possible to generate a selection which adheres to the rules.

Once confirmed, a shopping list is generated and saved in the directory `data/shoppingLists`. The list combines
ingredients together where possible, and includes the meals which called for each ingredient so that the user may have
the final say in what's required.

The `add_meal_to_diary` and `remove_dates_from_diary` scripts provide command-line utilities to manually add and remove
from the project diary.

`make_shopping_list` is a utility to make shopping lists using some subset of the `meal_diary.json` meal diary.

`check_recipe_definitions.py` checks that all recipes provided can be parsed as `Meal` objects. This checks the
vailidity of the user-provided meals. This script is ran as part of the project continuous integration build.

## Environment

Set up a new Python virtual environment, with a Python version conforming to the support versions specified in the
`pyproject.toml` file. Then install `poetry` if not already present on your machine (for example with `pip install
poetry`). Finally, run `poetry install` from the root directory to pull install the environment defined in the project's
`poetry.lock` file.
