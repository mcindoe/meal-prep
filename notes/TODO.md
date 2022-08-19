# TODO

- [ ] Rule to exclude a specified meal on a specified date
	- Used when we specify dates to change. We need to ensure that the same meal isn't specified again
	- For each (date, meal) pair rejected, we need to create a rule which excludes it from being recommended again, and then add it to the RuleCollection in use

- [ ] Regex for email addresses, and verify all email addresses on config load

- [ ] HEALTHY meal tag and rule

- [ ] Utility to display programmed meals, and ingredients to console / file
	- Display tags on the meals, check for spelling mistakes etc, check that ingredients are in appropriate categories

- [ ] Find out how to find the class name at runtime and use that to add a repr to BaseEnum, and remove it from all inherited classes