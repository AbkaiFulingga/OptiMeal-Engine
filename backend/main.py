from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import local modules
from models.user_preferences import UserPreferences
from models.recipe import Recipe
from models.meal_plan import MealPlan
from services.recipe_service import RecipeService
from services.optimization_service import OptimizationService
from services.meal_planner_service import MealPlannerService

app = FastAPI(
    title="OptiMeal Engine API",
    description="AI Smart Meal Planner + Grocery Optimizer API",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Welcome to OptiMeal Engine API"}

@app.post("/generate-meal-plan", response_model=MealPlan)
def generate_meal_plan(user_prefs: UserPreferences):
    """
    Generate an optimized meal plan based on user preferences and constraints
    """
    try:
        # Initialize services
        recipe_service = RecipeService()
        optimization_service = OptimizationService()
        meal_planner_service = MealPlannerService(recipe_service, optimization_service)
        
        # Generate the meal plan
        meal_plan = meal_planner_service.generate_meal_plan(user_prefs)
        
        return meal_plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recipes")
def get_recipes():
    """
    Get all available recipes
    """
    recipe_service = RecipeService()
    return recipe_service.get_all_recipes()

@app.get("/ingredients")
def get_ingredients():
    """
    Get all available ingredients with pricing
    """
    # Placeholder implementation
    return {"message": "Ingredients endpoint"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "localhost"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=True
    )