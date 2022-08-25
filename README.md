# Meal Prep

Specify dates, and shuffle a meal plan which adheres to the specified rules. Then generate a shopping list of the required ingredients.

## Usage

The user must define meals in the `Meals` enum in the file `src/meals.py`. Meals have associated *properties* and *tags*. A *property* is a key-value pair, and all properties should be provided for all meals. An example would be `meat=chicken`. A *tag* is a boolean flag which is taken to be True if present, and False otherwise, for example `Roast` or `Healthy`. The hope is that this framework allows for definitions of suitably arbitrary rules.

A `MealDiary` is a mapping from dates to meals. A rule is a filter applied to a meal collection, in the context of a date and a meal diary. This context is required to apply rules to a collection, for example for the rule "don't recommend the same meat on consecutive days" we need to know what the date in question is, and what meals have been had before and after that date (if any).

The config file `config.yaml` is used to specify runtime configuration, such as which dates to generate a meal plan for, and which rules to apply. The rules are specified by the name in the associated enum found in `src/rules.py`.

The main routine is at `src/main.py`. Running this file will run the program with the runtime configuration specified in the `config.yaml` file. A selection of meals which don't violate the specified rules are suggested, and the user is prompted to accept the plan or change meals on specified dates. Once rejected, a specified (date, meal) pair will not be recomended again. This process is re-run until the user confirms the selection, or until it is not possible to generate a selection which adheres to the rules.

Once confirmed, a shopping list is generated and saved in the directory `data/shoppingLists`. The list combines ingredients together where possible, and includes the meals which called for each ingredient so that the user may have the final say in what's required.

## Environment

* Tested using Python 3.9 and 3.10
* Set up a new Python virtual environment using the `requirements.txt` file
* Add the parent of the project's root directory `mealprep` to your `PYTHONPATH` environment variable
	- Test by running `from mealprep.src.meal import *` from a directory *not* containing `mealprep`
