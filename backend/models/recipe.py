from pydantic import BaseModel
from typing import List, Optional
from datetime import time


class Ingredient(BaseModel):
    name: str
    amount: float
    unit: str  # g, kg, ml, L, cup, tbsp, tsp, etc.
    cost_per_unit: float  # Cost per unit
    calories_per_unit: float
    protein_per_unit: float
    carbs_per_unit: float
    fat_per_unit: float


class Recipe(BaseModel):
    id: str
    name: str
    description: str
    ingredients: List[Ingredient]
    steps: List[str]
    cooking_time_min: int
    difficulty_level: str  # beginner, intermediate, advanced
    cuisine_type: str
    dietary_restrictions: List[str]  # vegetarian, vegan, etc.
    allergens: List[str]  # nuts, dairy, gluten, etc.
    
    # Nutritional information (total for the whole recipe)
    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float
    
    # Cost information
    total_cost: float