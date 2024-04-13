from __future__ import annotations

from collections.abc import Iterable
import copy
from typing import Iterator, Union

from mealprep.meal import Meal


class MealCollection:
    def __init__(self, meals: Iterable[Meal] = None):
        if meals is None:
            self.meals = tuple()
        else:
            self.meals = tuple(x for x in meals)

        if not all(isinstance(x, Meal) for x in self.meals):
            raise TypeError("All entries in 'meals' must be Meal instances")

    def copy(self) -> MealCollection:
        return MealCollection(copy.copy(self.meals))

    def __repr__(self) -> str:
        return f"MealCollection({self.meals!r})"

    def __len__(self) -> int:
        return len(self.meals)

    def __bool__(self) -> bool:
        return len(self) > 0

    def __iter__(self) -> Iterator[Meal]:
        return iter(self.meals)

    def __getitem__(self, index) -> Meal:
        return self.meals[index]

    def __add__(self, other: Union[Meal, MealCollection]) -> MealCollection:
        if isinstance(other, Meal):
            return MealCollection(self.meals + (other,))

        if isinstance(other, MealCollection):
            return MealCollection(self.meals + other.meals)

        raise TypeError("'other' must be one of Meal or MealCollection")

    def __eq__(self, other: MealCollection) -> bool:
        if not isinstance(other, MealCollection):
            return False

        if len(self) != len(other):
            return False

        for x in self:
            if x not in other:
                return False

        return True
