# TODO

- [ ] Unit Tests
	- Think carefully about this. Don't just assert what has been written. Think about what is expected implicitly

- [ ] DateInputGetter can be generalised. If no supported options are passed, then we can use standard formats such as YYYY-MM-DD. If supported options are passed, then that opens up other formats as options as already implemented

- [ ] HEALTHY meal tag and rule

- Helper Scripts
	- Displayed programmed meals, ingredients to console
	- Display tags on the meals, check for spelling mistakes etc, check that ingredients are in appropriate categories

- [ ] Move linuxMachineRequirements.txt out of the project repository
	- (Recall that the project runs with only a few dependencies)
	- Check what needs to be saved on the Linux machine and remove this file

- [ ] Bug: uncaught duplicate ingredient entries in a meal
	- [X] Add fix
	- [ ] Add unit test

- [ ] Unit test for IngredientQuantities that (Ingredient.X, BOOL, False) is not allowed

- [ ] Once we have changed Meals -> MealTemplates: update rule NotSameMealWithinSevenDays to be NotSameMainWithinSevenDays

- [ ] Unit tests for types in IngredientQuantityCollection initialiser
