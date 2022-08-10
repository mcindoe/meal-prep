# Project Design

## MVP: Command-line Generation of meals; reading and writing of meal diaries

- [ ] Ingredient
    - Name
    - Category

- [ ] Meal


- MealPlanner
    - Meal selection
    - Attributes:
        - Rules applied
        - Dates to select for
    - Has an emailer class as a member

- MealHistory
    - Loads from history file, which should be stored in a pickle file

- MealCollection
    - A collection of meals
    - Meals are validated as they're initialised

- Enums all over the place
