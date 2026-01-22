from typing import List
from models.recipe import Recipe
import json
import os


class RecipeService:
    def __init__(self, recipes_file_path: str = "../data/recipes.json"):
        """
        Initialize the recipe service with a path to the recipes data file
        """
        self.recipes_file_path = os.path.join(os.path.dirname(__file__), recipes_file_path)
        self._recipes = self._load_recipes()
    
    def _load_recipes(self) -> List[Recipe]:
        """
        Load recipes from the data file
        """
        # Check if the file exists, if not create a default one
        if not os.path.exists(self.recipes_file_path):
            self._create_default_recipes()
        
        try:
            with open(self.recipes_file_path, 'r') as f:
                recipes_data = json.load(f)
            
            recipes = []
            for recipe_data in recipes_data:
                # Convert dict to Recipe objects
                recipe = Recipe(**recipe_data)
                recipes.append(recipe)
            
            return recipes
        except FileNotFoundError:
            print(f"Recipes file not found at {self.recipes_file_path}")
            return []
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {self.recipes_file_path}")
            return []
    
    def _create_default_recipes(self):
        """
        Create a default recipes file if it doesn't exist
        """
        default_recipes = [
            {
                "id": "1",
                "name": "Vegetable Stir Fry",
                "description": "Quick and healthy vegetable stir fry",
                "ingredients": [
                    {
                        "name": "Broccoli",
                        "amount": 200,
                        "unit": "g",
                        "cost_per_unit": 0.01,
                        "calories_per_unit": 0.34,
                        "protein_per_unit": 0.028,
                        "carbs_per_unit": 0.066,
                        "fat_per_unit": 0.004
                    },
                    {
                        "name": "Bell Pepper",
                        "amount": 150,
                        "unit": "g",
                        "cost_per_unit": 0.02,
                        "calories_per_unit": 0.31,
                        "protein_per_unit": 0.009,
                        "carbs_per_unit": 0.06,
                        "fat_per_unit": 0.003
                    },
                    {
                        "name": "Soy Sauce",
                        "amount": 30,
                        "unit": "ml",
                        "cost_per_unit": 0.05,
                        "calories_per_unit": 1.02,
                        "protein_per_unit": 0.082,
                        "carbs_per_unit": 0.05,
                        "fat_per_unit": 0.001
                    }
                ],
                "steps": [
                    "Chop vegetables",
                    "Heat oil in pan",
                    "Add vegetables and stir fry for 5 minutes",
                    "Add soy sauce and cook for another 2 minutes"
                ],
                "cooking_time_min": 15,
                "difficulty_level": "beginner",
                "cuisine_type": "Asian",
                "dietary_restrictions": ["vegetarian", "vegan"],
                "allergens": [],
                "total_calories": 320,
                "total_protein_g": 15,
                "total_carbs_g": 35,
                "total_fat_g": 5,
                "total_cost": 4.50
            },
            {
                "id": "2",
                "name": "Grilled Chicken Salad",
                "description": "Fresh salad with grilled chicken",
                "ingredients": [
                    {
                        "name": "Chicken Breast",
                        "amount": 150,
                        "unit": "g",
                        "cost_per_unit": 0.12,
                        "calories_per_unit": 1.65,
                        "protein_per_unit": 0.31,
                        "carbs_per_unit": 0,
                        "fat_per_unit": 0.036
                    },
                    {
                        "name": "Lettuce",
                        "amount": 100,
                        "unit": "g",
                        "cost_per_unit": 0.03,
                        "calories_per_unit": 0.05,
                        "protein_per_unit": 0.014,
                        "carbs_per_unit": 0.029,
                        "fat_per_unit": 0.002
                    },
                    {
                        "name": "Tomato",
                        "amount": 120,
                        "unit": "g",
                        "cost_per_unit": 0.04,
                        "calories_per_unit": 0.18,
                        "protein_per_unit": 0.009,
                        "carbs_per_unit": 0.039,
                        "fat_per_unit": 0.002
                    }
                ],
                "steps": [
                    "Season chicken breast and grill for 6-7 minutes each side",
                    "Chop lettuce and tomatoes",
                    "Combine ingredients in a bowl",
                    "Add dressing of choice"
                ],
                "cooking_time_min": 20,
                "difficulty_level": "beginner",
                "cuisine_type": "American",
                "dietary_restrictions": ["gluten_free"],
                "allergens": [],
                "total_calories": 420,
                "total_protein_g": 45,
                "total_carbs_g": 12,
                "total_fat_g": 15,
                "total_cost": 7.20
            }
        ]
        
        # Create the data directory if it doesn't exist
        os.makedirs(os.path.dirname(self.recipes_file_path), exist_ok=True)
        
        with open(self.recipes_file_path, 'w') as f:
            json.dump(default_recipes, f, indent=2)
    
    def get_all_recipes(self) -> List[Recipe]:
        """
        Return all available recipes
        """
        return self._recipes
    
    def get_recipe_by_id(self, recipe_id: str) -> Recipe:
        """
        Get a specific recipe by ID
        """
        for recipe in self._recipes:
            if recipe.id == recipe_id:
                return recipe
        return None
    
    def filter_recipes(self, **filters) -> List[Recipe]:
        """
        Filter recipes based on various criteria
        """
        filtered_recipes = self._recipes
        
        # Apply filters
        if 'dietary_restrictions' in filters and filters['dietary_restrictions']:
            req_dietary = set(filters['dietary_restrictions'])
            filtered_recipes = [
                r for r in filtered_recipes
                if req_dietary.issubset(set(r.dietary_restrictions))
            ]
        
        if 'allergens' in filters and filters['allergens']:
            allergens_to_avoid = set(filters['allergens'])
            filtered_recipes = [
                r for r in filtered_recipes
                if not allergens_to_avoid.intersection(set(r.allergens))
            ]
        
        if 'max_cooking_time' in filters:
            max_time = filters['max_cooking_time']
            filtered_recipes = [
                r for r in filtered_recipes
                if r.cooking_time_min <= max_time
            ]
        
        if 'cuisine_types' in filters and filters['cuisine_types']:
            allowed_cuisines = set(filters['cuisine_types'])
            filtered_recipes = [
                r for r in filtered_recipes
                if r.cuisine_type in allowed_cuisines
            ]
        
        return filtered_recipes