#! /usr/bin/bash

black . --line-length 100 --check
isort . --check --line-length 100 --multi-line 3 --lines-after-imports 2 --force-sort-within-sections --dont-order-by-type --trailing-comma
python -m mealprep.routines.ci.check_ingredient_definitions
python -m mealprep.routines.ci.check_recipe_definitions
