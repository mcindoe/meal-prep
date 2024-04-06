from __future__ import annotations

import collections
from collections.abc import Iterable
from typing import Any, Optional, Union

from mealprep.constants import MealMetadata, MealProperty, MealTag
from mealprep.ingredient import IngredientQuantityCollection


class Meal:
    def __init__(
        self,
        name: str,
        ingredient_quantities: IngredientQuantityCollection,
        properties: dict[MealProperty, Any],
        tags: Optional[Union[MealTag, Iterable[MealTag]]] = None,
    ):
        self.name = name
        self.ingredient_quantities = IngredientQuantityCollection(ingredient_quantities)

        if not isinstance(name, str):
            raise TypeError("'name' argument must be a string in Meal init")

        if not isinstance(properties, dict):
            raise TypeError("'properties' argument must be a dict in Meal init")

        if not all(isinstance(x, MealProperty) for x in properties):
            raise TypeError("All keys in 'properties' dictionary must be MealProperties")

        missing_properties = tuple(x for x in MealProperty if x not in properties.keys())
        if missing_properties:
            raise ValueError(f"Unspecified properties in Meal construction: {missing_properties}")

        # There should not be more than one entry of a given ingredient
        # in the passed ingredient_quantities collection
        if ingredient_quantities:
            if max(collections.Counter(x.ingredient for x in ingredient_quantities).values()) > 1:
                raise ValueError("Passed multiple entries of the same ingredient in Meal init")

        if tags is None:
            tags = ()

        if tags is not None:
            if isinstance(tags, MealTag):
                tags = (tags,)

            tags = set(tags)

            for x in tags:
                if not isinstance(x, MealTag):
                    raise ValueError(f"{x} is not a MealTag in Meal init")

        self.metadata = properties.copy()

        for tag in MealTag:
            self.metadata[tag] = tag in tags

    def __repr__(self) -> str:
        return f'Meal(name="{self.name}")'

    def __getitem__(self, key: MealMetadata) -> Any:
        if not isinstance(key, MealMetadata):
            raise TypeError("'key' must be a MealMetadata instance")
        return self.metadata[key]

    def __eq__(self, other: Meal) -> bool:
        return all(
            (
                self.name == other.name,
                self.ingredient_quantities == other.ingredient_quantities,
                self.metadata == other.metadata,
            )
        )

    def __hash__(self) -> int:
        return hash(f"Meal('{self.name}')")
