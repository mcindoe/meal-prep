# TODO

- [ ] Check through the source code for anywhere where we could be iterating directly over a Collection, but are instead using the old implementation of iterating directly over its elements.

- [ ] DateInputGetter can be generalised. If no supported options are passed, then we can use standard formats such as YYYY-MM-DD. If supported options are passed, then that opens up other formats as options as already implemented

- [ ] Regex for email addresses, and verify all email addresses on config load

- [ ] HEALTHY meal tag and rule

- [ ] Utility to display programmed meals, and ingredients to console / file
	- Display tags on the meals, check for spelling mistakes etc, check that ingredients are in appropriate categories

- [ ] Test that any requirements.txt are required. This project runs with vanilla python right?
	- Check on the home machine. I think I just need neovim installed for my purposes. Perhaps a python linter as well, but this shouldn't be part of the project setup configuration

- [ ] Bug: uncaught duplicate ingredient entries in a meal. Test and fix. Unit tests required.

- [ ] Unit test for IngredientQuantities that (Ingredient.X, BOOL, False) is not allowed

- [ ] Once we have changed Meals -> MealTemplates: update rule NotSameMealWithinSevenDays to be NotSameMainWithinSevenDays

- [ ] Unit tests for types in IngredientQuantityCollection initialiser
