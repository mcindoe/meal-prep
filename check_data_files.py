from utils import load_meals

SUPPORTED_PROTEINS = [
    'beef',
    'fish',
    'pork',
    'chicken',
    'lamb'
]

def check_meals():
    meals = load_meals()
    errors_found = False

    print('\nChecking meals.json for errors')

    # we expect to have a protein entry for every meal, and those
    # protein values to be presented in the SUPPORTED_PROTEINS list above
    for meal, meal_info in meals.items():
        if 'protein' not in meal_info:
            errors_found = True
            print(f'{meal} is missing a protein entry')

        else:
            protein = meal_info['protein']
            if protein not in SUPPORTED_PROTEINS:
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

if __name__ == '__main__':
    check_meals()


