from pydantic import BaseModel
from typing import List, Dict
from datetime import date
from models.recipe import Recipe


class Meal(BaseModel):
    day: str  # Monday, Tuesday, etc.
    meal_type: str  # breakfast, lunch, dinner, snack
    recipe: Recipe


class DailyMeals(BaseModel):
    date: date
    meals: List[Meal]


class MealPlan(BaseModel):
    week_start_date: date
    daily_meals: List[DailyMeals]
    total_cost: float
    nutritional_summary: Dict[str, float]  # Total macros for the week
    grocery_list: List[Dict[str, float]]  # Ingredient to quantity mapping