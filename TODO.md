# TODO

- [ ] Unit Tests
	- Think carefully about this. Don't just assert what has been written. Think about what is expected implicitly
	- [ ] Test for IngredientQuantities that (Ingredient.X, BOOL, False) is not allowed
	- [ ] Tests for types in IngredientQuantityCollection initialiser

- [ ] Consolidate old meals file
	- [X] Copy old meals into new structure
	- [ ] Remove old file
		- I'm going to wait to confirm meals before doing this. Perhaps with the help of helper scripts

- [ ] Check phone for other tasks

- [ ] DateInputGetter can be generalised. If no supported options are passed, then we can use standard formats such as YYYY-MM-DD. If supported options are passed, then that opens up other formats as options as already implemented

- [ ] HEALTHY meal tag and rule

- [ ] Move linuxMachineRequirements.txt out of the project repository
	- (Recall that the project runs with only a few dependencies)
	- Check what needs to be saved on the Linux machine and remove this file

- [ ] Bug: uncaught duplicate ingredient entries in a meal
	- [X] Add fix
	- [ ] Add unit test
