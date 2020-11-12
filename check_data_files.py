from utils import load_ingredients
from utils import load_meals

MEALS_SUPPORTED_PROTEINS = [
    'beef',
    'fish',
    'pork',
    'chicken',
    'lamb',
]

INGREDIENTS_SUPPORTED_KEYS = [
    'category',
    'measured_in',
    'unit',
]

INGREDIENTS_SUPPORTED_CATEGORIES = [
    'carbohydrate',
    'condiment',
    'dairy',
    'fish',
    'herb',
    'meat',
    'other',
    'sauce',
    'spice',
    'tins',
    'vegetable',
]

INGREDIENTS_SUPPORTED_MEASURED_IN = [
    'units',
    'bool',
    'grams',
    'ml'
]

def check_meals():
    meals = load_meals()
    errors_found = False

    print('\nChecking meals.json for errors')

    # we expect to have a protein entry for every meal, and those
    # protein values to be presented in the MEALS_SUPPORTED_PROTEINS list above
    for meal, meal_info in meals.items():
        if 'protein' not in meal_info:
            errors_found = True
            print(f'{meal} is missing a protein entry')

        else:
            protein = meal_info['protein']
            if protein not in MEALS_SUPPORTED_PROTEINS:
                errors_found = True
                print(f'{meal} has an unsupported protein option {protein}')

    # we expect to all meal info keys and value strings to be lower case
    for meal, meal_info in meals.items():
        for key, val in meal_info.items():
            if key != key.lower():
                errors_found = True
                print(f'{meal} has a key {key} instead of {key.lower()}')

            if isinstance(val, str) and val != val.lower():
                errors_found = True
                print(f'{meal} has a value {val} instead of {val.lower()} for {key}')

    # we expect all 'favourite' entries to be boolean values
    for meal, meal_info in meals.items():
        if 'favourite' in meal_info.keys():
            favourite = meal_info['favourite']
            if not isinstance(favourite, bool):
                errors_found = True
                print(f'{meal} has a non-boolean favourite entry. Found {favourite}')

    if not errors_found:
        print('No errors found')
    print()


def check_ingredients():
    ingredients = load_ingredients()
    errors_found = False

    print('\nChecking meals.json for errors')

    for name, info in ingredients.items():
        for key in info.keys():
            if key not in INGREDIENTS_SUPPORTED_KEYS:
                errors_found = True
                print(f'{name} has an unsupported key {key}')

        if 'category' not in info.keys():
            errors_found = True
            print(f'{name} has no category key')
        else:
            category = info['category']
            if category not in INGREDIENTS_SUPPORTED_CATEGORIES:
                errors_found = True
                print(f'{name} has an unsupported category {category}')
        
        if 'measured_in' not in info.keys():
            errors_found = True
            print(f'{name} has no measured_in key')
        else:
            measured_in = info['measured_in']
            if measured_in not in INGREDIENTS_SUPPORTED_MEASURED_IN:
                errors_found = True
                print(f'{name} has an unsupported measured_in value {measured_in}')

    if not errors_found:
        print('No errors found')
    print()


if __name__ == '__main__':
    check_ingredients()
    check_meals()


