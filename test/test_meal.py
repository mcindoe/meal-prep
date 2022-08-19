import pytest

from mealprep.src.constants import MealMeat
from mealprep.src.constants import MealProperty
from mealprep.src.constants import MealTag
from mealprep.src.constants import Unit
from mealprep.src.ingredient import IngredientQuantity
from mealprep.src.ingredient import IngredientQuantityCollection
from mealprep.src.ingredient import Ingredients
from mealprep.src.meal import Meal
from mealprep.src.meal import MealCollection
from mealprep.src.meal import MealDiary


class TestMeal:
    def test_initialiser_errors(self):
        # Name is not a string
        with pytest.raises(TypeError):
            Meal(
                name=42,
                ingredient_quantities=(
                    IngredientQuantity(Ingredients.BAY_LEAVES, Unit.BOOL, True),
                    IngredientQuantity(Ingredients.CARROT, Unit.NUMBER, 1),
                ),
                properties={},
                tags=(MealTag.PASTA,)
            )

        # Ingredient Quantities contains non-Ingredients
        with pytest.raises(TypeError):
            Meal(
                name="Meal Name",
                ingredient_quantities=(
                    "300g of Carrot",
                ),
                properties={
                    MealProperty.MEAT: MealMeat.BEEF
                },
                tags=(MealTag.PASTA,)
            )

        # Properties not a dictionary
        with pytest.raises(TypeError):
            Meal(
                name="Meal Name",
                ingredient_quantities=(
                    IngredientQuantity(Ingredients.BAY_LEAVES, Unit.BOOL, True),
                    IngredientQuantity(Ingredients.CARROT, Unit.NUMBER, 1),
                ),
                properties=(MealMeat.BEEF,),
                tags=(MealTag.PASTA,)
            )

        # Missing properties
        with pytest.raises(ValueError):
            Meal(
                name="Meal Name",
                ingredient_quantities=(
                    IngredientQuantity(Ingredients.BAY_LEAVES, Unit.BOOL, True),
                    IngredientQuantity(Ingredients.CARROT, Unit.NUMBER, 1),
                ),
                properties={},
                tags=(MealTag.PASTA,)
            )

        # Tags argument contains non-Tags
        with pytest.raises(ValueError):
            Meal(
                name="Meal Name",
                ingredient_quantities=(
                    IngredientQuantity(Ingredients.BAY_LEAVES, Unit.BOOL, True),
                    IngredientQuantity(Ingredients.CARROT, Unit.NUMBER, 1),
                ),
                properties={
                    MealProperty.MEAT: MealMeat.BEEF
                },
                tags=("PASTA",)
            )

    def test_getters(self):
        x = Meal(
            name="Meal Name",
            ingredient_quantities=(
                IngredientQuantity(Ingredients.BAY_LEAVES, Unit.BOOL, True),
                IngredientQuantity(Ingredients.CARROT, Unit.NUMBER, 1),
            ),
            properties={
                MealProperty.MEAT: MealMeat.BEEF
            },
            tags=(MealTag.PASTA,)
        )

        assert x.name == "Meal Name"
        assert isinstance(x.ingredient_quantities, IngredientQuantityCollection)
        assert x[MealProperty.MEAT] is MealMeat.BEEF
        assert x[MealTag.PASTA]
        assert not x[MealTag.VEGETARIAN]

        chinese_pork_belly = Meal.from_name("Sticky Chinese Pork Belly")
        assert chinese_pork_belly[MealProperty.MEAT] is MealMeat.PORK
        assert not chinese_pork_belly[MealTag.VEGETARIAN]

        # Construction from a single tag
        Meal(
            name="Meal Name",
            ingredient_quantities=(),
            properties={
                MealProperty.MEAT: MealMeat.BEEF
            },
            tags=MealTag.PASTA
        )



class TestMealCollection:
    def test_initialiser(self):
        meals = (
            Meal.from_name("Spaghetti Bolognese"),
            Meal.from_name("Sticky Chinese Pork Belly")
        )
        meal_collection = MealCollection(meals)

        # MealCollections should maintain their own copy of their meals
        assert meal_collection.meals is not meals

    def from_supported_meals(self):
        """Test that we can load meals from the project supported specification"""

        x = MealCollection.from_supported_meals()
        assert isinstance(x, MealCollection)
