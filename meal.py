'''
Provides the Meal class, which represents
a meal with all the trimmings
'''

import utils

class Meal:
    def __init__(self, name, vegetables=None):
        self.name = name
        self.vegetables = vegetables

    def __repr__(self):
        if self.vegetables is None:
            return f'Meal({self.name})'
        return f'Meal({self.name}, {self.vegetables})'

    def __str__(self):
        if self.vegetables is None:
            return self.name
        return f'{self.name} with {utils.make_list_str(self.vegetables)}'

    @property
    def ingredients(self):
        meals = utils.load_meals()

        ingredients = meals[self.name]['ingredients']
        if self.vegetables is not None:
            for veg in self.vegetables:
                ingredients[veg] = True

        return ingredients

    def to_json(self):
        return {
            'name': self.name,
            'vegetables': self.vegetables
        }

    @staticmethod
    def from_json(meal_info):
        name = meal_info['name']
        vegetables = meal_info['vegetables']
        return Meal(name, vegetables)
