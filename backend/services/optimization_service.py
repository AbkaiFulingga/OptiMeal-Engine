from ortools.linear_solver import pywraplp
from typing import List, Dict, Tuple
from models.recipe import Recipe
from models.user_preferences import UserPreferences


class OptimizationService:
    def __init__(self):
        """
        Initialize the optimization service
        """
        pass
    
    def optimize_meal_plan(
        self,
        recipes: List[Recipe],
        user_preferences: UserPreferences,
        days: int = 7
    ) -> List[Tuple[Recipe, int]]:
        """
        Optimize the meal plan based on user preferences and constraints using multi-objective optimization
        Returns a list of (recipe, servings) tuples
        """
        # Create the solver
        solver = pywraplp.Solver.CreateSolver('SCIP')
        if not solver:
            raise Exception('Could not create solver SCIP')

        # Define decision variables: x[i] = number of servings of recipe i
        num_recipes = len(recipes)
        x = {}
        for i in range(num_recipes):
            x[i] = solver.IntVar(0, 10, f'x[{i}]')  # Max 10 servings per recipe

        # Calculate weekly nutritional targets
        weekly_protein_target = user_preferences.target_protein_g * days if user_preferences.target_protein_g else 0
        weekly_carbs_target = user_preferences.target_carbs_g * days if user_preferences.target_carbs_g else 0
        weekly_fat_target = user_preferences.target_fat_g * days if user_preferences.target_fat_g else 0
        weekly_calories_target = user_preferences.target_calories * days if user_preferences.target_calories else 0

        # Add constraints
        # 1. Nutritional constraints
        if weekly_protein_target > 0:
            solver.Add(
                sum(x[i] * recipes[i].total_protein_g for i in range(num_recipes)) >= weekly_protein_target * 0.8
            )  # Allow 20% flexibility
            solver.Add(
                sum(x[i] * recipes[i].total_protein_g for i in range(num_recipes)) <= weekly_protein_target * 1.2
            )

        if weekly_carbs_target > 0:
            solver.Add(
                sum(x[i] * recipes[i].total_carbs_g for i in range(num_recipes)) >= weekly_carbs_target * 0.8
            )
            solver.Add(
                sum(x[i] * recipes[i].total_carbs_g for i in range(num_recipes)) <= weekly_carbs_target * 1.2
            )

        if weekly_fat_target > 0:
            solver.Add(
                sum(x[i] * recipes[i].total_fat_g for i in range(num_recipes)) >= weekly_fat_target * 0.8
            )
            solver.Add(
                sum(x[i] * recipes[i].total_fat_g for i in range(num_recipes)) <= weekly_fat_target * 1.2
            )

        if weekly_calories_target > 0:
            solver.Add(
                sum(x[i] * recipes[i].total_calories for i in range(num_recipes)) >= weekly_calories_target * 0.8
            )
            solver.Add(
                sum(x[i] * recipes[i].total_calories for i in range(num_recipes)) <= weekly_calories_target * 1.2
            )

        # 2. Budget constraint
        solver.Add(
            sum(x[i] * recipes[i].total_cost for i in range(num_recipes)) <= user_preferences.weekly_budget
        )

        # 3. Variety constraint: no recipe more than max_repeats_per_week times per week
        for i in range(num_recipes):
            solver.Add(x[i] <= user_preferences.max_repeats_per_week)

        # 4. Meal frequency constraint: ensure enough meals per day
        min_meals_per_day = 3  # Breakfast, lunch, dinner
        min_total_meals = min_meals_per_day * days
        solver.Add(sum(x[i] for i in range(num_recipes)) >= min_total_meals)

        # 5. Cooking time constraint
        solver.Add(
            sum(x[i] * recipes[i].cooking_time_min for i in range(num_recipes)) <=
            min_meals_per_day * days * user_preferences.max_cooking_time_min
        )

        # Define a weighted objective function combining multiple goals:
        # Minimize cost, maximize nutrition target satisfaction, minimize waste
        # Using a weighted sum approach
        cost_component = sum(x[i] * recipes[i].total_cost for i in range(num_recipes))

        # Nutrition deviation penalty (penalize deviation from targets)
        protein_deviation = 0
        carbs_deviation = 0
        fat_deviation = 0
        calories_deviation = 0

        if weekly_protein_target > 0:
            actual_protein = sum(x[i] * recipes[i].total_protein_g for i in range(num_recipes))
            protein_deviation = abs(actual_protein - weekly_protein_target)

        if weekly_carbs_target > 0:
            actual_carbs = sum(x[i] * recipes[i].total_carbs_g for i in range(num_recipes))
            carbs_deviation = abs(actual_carbs - weekly_carbs_target)

        if weekly_fat_target > 0:
            actual_fat = sum(x[i] * recipes[i].total_fat_g for i in range(num_recipes))
            fat_deviation = abs(actual_fat - weekly_fat_target)

        if weekly_calories_target > 0:
            actual_calories = sum(x[i] * recipes[i].total_calories for i in range(num_recipes))
            calories_deviation = abs(actual_calories - weekly_calories_target)

        nutrition_penalty = (protein_deviation + carbs_deviation + fat_deviation + calories_deviation) * 0.1  # Weight for nutrition

        # Total objective: minimize cost + nutrition penalties
        objective_expr = cost_component + nutrition_penalty

        # Since OR-Tools only supports linear objectives, we'll use a simpler approach
        # Minimize cost as primary objective, with nutrition constraints as hard constraints
        objective = solver.Objective()
        for i in range(num_recipes):
            objective.SetCoefficient(x[i], recipes[i].total_cost)
        objective.SetMinimization()

        # Solve the problem
        status = solver.Solve()

        if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
            result = []
            for i in range(num_recipes):
                servings = x[i].solution_value()
                if servings > 0:
                    result.append((recipes[i], int(servings)))
            return result
        else:
            # If no optimal solution found, try relaxing constraints progressively
            return self._relax_and_solve(solver, recipes, x, user_preferences, days)

    def _relax_and_solve(self, solver, recipes, x, user_preferences, days):
        """
        Helper method to relax constraints if the original problem is infeasible
        """
        # Relax nutrition constraints slightly
        # This is a simplified approach - in practice, you might want more sophisticated relaxation
        original_constraints = solver.NumConstraints()

        # Try solving with relaxed nutrition constraints (allow 30% deviation instead of 20%)
        # We'd need to recreate the constraints here, so for now return empty result
        # In a full implementation, we would have a more sophisticated constraint relaxation system
        print("Could not find solution with current constraints. Consider relaxing some requirements.")
        return []
    
    def calculate_grocery_list(self, meal_plan: List[Tuple[Recipe, int]]) -> Dict[str, float]:
        """
        Calculate the grocery list from the optimized meal plan
        """
        grocery_list = {}
        
        for recipe, servings in meal_plan:
            for ingredient in recipe.ingredients:
                ingredient_key = f"{ingredient.name} ({ingredient.unit})"
                total_amount = ingredient.amount * servings
                
                if ingredient_key in grocery_list:
                    grocery_list[ingredient_key] += total_amount
                else:
                    grocery_list[ingredient_key] = total_amount
        
        return grocery_list