from typing import List
from models.user_preferences import UserPreferences
from models.meal_plan import MealPlan, DailyMeals, Meal
from models.recipe import Recipe
from services.recipe_service import RecipeService
from services.optimization_service import OptimizationService
from services.grocery_optimizer_service import GroceryOptimizerService
from datetime import date, timedelta
import random


class MealPlannerService:
    def __init__(
        self,
        recipe_service: RecipeService,
        optimization_service: OptimizationService
    ):
        self.recipe_service = recipe_service
        self.optimization_service = optimization_service
        self.grocery_optimizer = GroceryOptimizerService()
    
    def generate_meal_plan(self, user_preferences: UserPreferences) -> MealPlan:
        """
        Generate a complete meal plan based on user preferences
        """
        # Filter recipes based on user preferences
        filtered_recipes = self.recipe_service.filter_recipes(
            dietary_restrictions=user_preferences.dietary_restrictions,
            allergens=user_preferences.allergies,
            max_cooking_time=user_preferences.max_cooking_time_min,
            cuisine_types=user_preferences.preferred_cuisines
        )

        if not filtered_recipes:
            raise ValueError("No recipes match your preferences and constraints")

        # Optimize the meal plan
        optimized_plan = self.optimization_service.optimize_meal_plan(
            recipes=filtered_recipes,
            user_preferences=user_preferences
        )

        if not optimized_plan:
            raise ValueError("Could not generate a meal plan within your constraints")

        # Create daily meal plans from the optimized plan
        daily_meals = self._create_daily_meals(optimized_plan, user_preferences)

        # Calculate grocery list
        grocery_list = self.optimization_service.calculate_grocery_list(optimized_plan)

        # Calculate total cost
        total_cost = sum(recipe.total_cost * servings for recipe, servings in optimized_plan)

        # Calculate nutritional summary
        nutritional_summary = self._calculate_nutritional_summary(optimized_plan)

        # Optimize the grocery list for store selection and cost
        optimized_grocery = self.grocery_optimizer.optimize_grocery_list(
            grocery_list,
            user_preferences,
            single_store_mode=True  # Default to single store mode
        )

        # Create the meal plan object
        today = date.today()
        # Find the upcoming Monday
        days_until_monday = (7 - today.weekday()) % 7
        if days_until_monday == 0:  # If today is Monday
            days_until_monday = 7
        week_start_date = today + timedelta(days=days_until_monday)

        meal_plan = MealPlan(
            week_start_date=week_start_date,
            daily_meals=daily_meals,
            total_cost=optimized_grocery["total_cost"],
            nutritional_summary=nutritional_summary,
            grocery_list=optimized_grocery
        )

        return meal_plan
    
    def _create_daily_meals(
        self,
        optimized_plan: List[tuple],
        user_preferences: UserPreferences
    ) -> List[DailyMeals]:
        """
        Distribute the optimized recipes across the week using rolling horizon planning
        and ingredient reuse optimization
        """
        daily_meals = []
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        # Create a list of recipe assignments based on servings
        recipe_assignments = []
        for recipe, servings in optimized_plan:
            for _ in range(int(servings)):
                recipe_assignments.append(recipe)

        # Implement rolling horizon planning with ingredient reuse consideration
        assigned_recipes = [None] * (len(days) * 3)  # 3 meals per day

        # Track used ingredients to promote reuse
        ingredient_usage_tracker = {}

        # For each day, assign recipes considering ingredient overlap
        for day_idx in range(len(days)):
            # Get potential recipes for this day (filter out those that exceed max repeats)
            day_start_idx = day_idx * 3
            day_end_idx = day_start_idx + 3

            for meal_pos in range(day_start_idx, day_end_idx):
                if recipe_assignments:  # If we still have recipes to assign
                    # Score available recipes based on ingredient reuse and variety
                    scored_recipes = []
                    for i, recipe in enumerate(recipe_assignments):
                        score = self._score_recipe_for_assignment(recipe, ingredient_usage_tracker, user_preferences)
                        scored_recipes.append((score, i, recipe))

                    # Sort by score (higher is better)
                    scored_recipes.sort(key=lambda x: x[0], reverse=True)

                    # Take the highest scoring recipe
                    if scored_recipes:
                        _, recipe_idx, selected_recipe = scored_recipes[0]

                        # Update ingredient tracker
                        for ingredient in selected_recipe.ingredients:
                            ing_name = ingredient.name
                            if ing_name in ingredient_usage_tracker:
                                ingredient_usage_tracker[ing_name] += 1
                            else:
                                ingredient_usage_tracker[ing_name] = 1

                        # Assign the recipe
                        assigned_recipes[meal_pos] = selected_recipe
                        # Remove the assigned recipe from available recipes
                        recipe_assignments.pop(recipe_idx)

        # Convert to the expected format
        for day_idx, day in enumerate(days):
            day_start_idx = day_idx * 3
            day_meals = []

            meal_types = ["breakfast", "lunch", "dinner"]
            for meal_pos_offset, meal_type in enumerate(meal_types):
                meal_idx = day_start_idx + meal_pos_offset
                if meal_idx < len(assigned_recipes) and assigned_recipes[meal_idx] is not None:
                    recipe = assigned_recipes[meal_idx]
                    day_meals.append(Meal(
                        day=day,
                        meal_type=meal_type,
                        recipe=recipe
                    ))

            daily_meals.append(DailyMeals(
                date=date.today() + timedelta(days=(day_idx + (7 - date.today().weekday()) % 7)),
                meals=day_meals
            ))

        return daily_meals

    def _score_recipe_for_assignment(self, recipe, ingredient_usage_tracker, user_preferences):
        """
        Score a recipe for assignment based on ingredient reuse, variety, and other factors
        """
        score = 0

        # Positive score for ingredient reuse (using ingredients we already have)
        reuse_bonus = 0
        for ingredient in recipe.ingredients:
            if ingredient.name in ingredient_usage_tracker:
                reuse_bonus += 1  # Bonus for reusing ingredients

        # Negative score for exceeding variety constraints
        variety_penalty = 0
        # This would be more complex in a full implementation

        # Positive score for meeting macro targets
        macro_alignment = 0
        # This would consider how well the recipe fits the remaining macro needs

        score = reuse_bonus * 10 - variety_penalty * 5 + macro_alignment * 2

        return score
    
    def _calculate_nutritional_summary(self, optimized_plan: List[tuple]) -> dict:
        """
        Calculate the total nutritional values for the week
        """
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        total_calories = 0
        
        for recipe, servings in optimized_plan:
            total_protein += recipe.total_protein_g * servings
            total_carbs += recipe.total_carbs_g * servings
            total_fat += recipe.total_fat_g * servings
            total_calories += recipe.total_calories * servings
        
        return {
            "total_protein_g": total_protein,
            "total_carbs_g": total_carbs,
            "total_fat_g": total_fat,
            "total_calories": total_calories
        }