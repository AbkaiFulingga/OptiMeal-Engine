from pydantic import BaseModel
from typing import List, Optional
from enum import Enum


class DietaryRestriction(str, Enum):
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    KETO = "keto"
    PALEO = "paleo"
    HALAL = "halal"
    KOSHER = "kosher"
    GLUTEN_FREE = "gluten_free"
    DAIRY_FREE = "dairy_free"


class CookingSkillLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class UserPreferences(BaseModel):
    # Dietary constraints
    dietary_restrictions: List[DietaryRestriction] = []
    allergies: List[str] = []  # List of allergens
    dislikes: List[str] = []   # Foods to avoid
    
    # Nutritional goals (daily)
    target_protein_g: Optional[int] = None
    target_carbs_g: Optional[int] = None
    target_fat_g: Optional[int] = None
    target_calories: Optional[int] = None
    
    # Preferences
    preferred_cuisines: List[str] = []
    cooking_skill_level: CookingSkillLevel = CookingSkillLevel.INTERMEDIATE
    max_cooking_time_min: int = 60  # Maximum cooking time per meal
    
    # Budget constraints
    weekly_budget: float  # Total budget for the week
    
    # Variety preferences
    max_repeats_per_week: int = 2  # Max times a recipe can appear in a week