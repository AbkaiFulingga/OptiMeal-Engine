import openai
from typing import List, Dict, Optional
from models.recipe import Recipe, Ingredient
from utils.ingredient_utils import normalize_ingredient_name, is_valid_ingredient, standardize_units
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class RecipeGeneratorService:
    def __init__(self):
        """
        Initialize the recipe generator service
        Note: This service uses OpenAI API for recipe generation
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            openai.api_key = api_key
            self.use_llm = True
        else:
            print("OpenAI API key not found. Recipe generation will use mock data.")
            self.use_llm = False
    
    def generate_recipe(
        self,
        dish_name: str,
        dietary_restrictions: List[str] = [],
        allergens: List[str] = [],
        cuisine_type: str = "",
        cooking_time: int = 60
    ) -> Optional[Recipe]:
        """
        Generate a recipe using LLM with strict validation to prevent hallucination
        """
        if not self.use_llm:
            # Return a mock recipe for demonstration purposes
            return self._create_mock_recipe(dish_name, dietary_restrictions, allergens, cuisine_type, cooking_time)
        
        try:
            # Create a prompt for the LLM to generate a recipe skeleton
            prompt = self._create_generation_prompt(
                dish_name, dietary_restrictions, allergens, cuisine_type, cooking_time
            )
            
            # Call the OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful recipe assistant. Generate recipes with realistic ingredients and cooking instructions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Parse the response
            recipe_data = self._parse_llm_response(response.choices[0].message.content)
            
            # Validate the recipe to prevent hallucination
            validated_recipe = self._validate_and_correct_recipe(recipe_data)
            
            return validated_recipe
        except Exception as e:
            print(f"Error generating recipe: {str(e)}")
            return None
    
    def _create_generation_prompt(
        self,
        dish_name: str,
        dietary_restrictions: List[str],
        allergens: List[str],
        cuisine_type: str,
        cooking_time: int
    ) -> str:
        """
        Create a prompt for the LLM to generate a recipe
        """
        prompt = f"""
        Generate a recipe for {dish_name}.
        """
        
        if dietary_restrictions:
            prompt += f"Dietary restrictions: {', '.join(dietary_restrictions)}. "
        
        if allergens:
            prompt += f"Avoid these allergens: {', '.join(allergens)}. "
        
        if cuisine_type:
            prompt += f"Cuisine type: {cuisine_type}. "
        
        prompt += f"Maximum cooking time: {cooking_time} minutes. "
        
        prompt += """
        Respond in the following JSON format:
        {
            "name": "Recipe Name",
            "description": "Brief description of the dish",
            "ingredients": [
                {
                    "name": "ingredient name",
                    "amount": numeric amount,
                    "unit": "unit of measurement (g, kg, ml, L, cup, tbsp, tsp, oz, lb)",
                    "notes": "optional notes about the ingredient"
                }
            ],
            "steps": [
                "Step 1",
                "Step 2",
                ...
            ],
            "cooking_time_min": integer cooking time in minutes,
            "difficulty_level": "beginner|intermediate|advanced",
            "cuisine_type": "cuisine type",
            "dietary_restrictions": ["list", "of", "dietary", "restrictions"],
            "allergens": ["list", "of", "potential", "allergens"]
        }
        
        Make sure all ingredients are real and commonly available. Do not invent fictional ingredients.
        """
        
        return prompt
    
    def _parse_llm_response(self, response_text: str) -> Dict:
        """
        Parse the LLM response to extract recipe data
        """
        # Try to find JSON in the response
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        
        if start_idx != -1 and end_idx != 0:
            json_str = response_text[start_idx:end_idx]
            try:
                recipe_data = json.loads(json_str)
                return recipe_data
            except json.JSONDecodeError:
                print("Could not parse JSON from LLM response")
                return {}
        else:
            print("No JSON found in LLM response")
            return {}
    
    def _validate_and_correct_recipe(self, recipe_data: Dict) -> Optional[Recipe]:
        """
        Validate the recipe to ensure all ingredients exist in our database
        and correct any hallucinated ingredients
        """
        if not recipe_data:
            return None
        
        # Validate and correct ingredients
        validated_ingredients = []
        for ing_data in recipe_data.get('ingredients', []):
            ingredient_name = normalize_ingredient_name(ing_data['name'])
            
            # Check if ingredient exists in our database
            if is_valid_ingredient(ingredient_name):
                # Get standard unit and cost from our database
                standard_ing = self._get_ingredient_from_db(ingredient_name)
                
                # Standardize units
                amount, unit = standardize_units(ingredient_name, ing_data['amount'], ing_data['unit'])
                
                # Calculate cost, calories, and macros based on our database
                cost = amount * standard_ing['avg_cost_per_unit']
                calories = (amount / 100) * standard_ing['calories_per_100g']
                protein = (amount / 100) * standard_ing['protein_per_100g']
                carbs = (amount / 100) * standard_ing['carbs_per_100g']
                fat = (amount / 100) * standard_ing['fat_per_100g']
                
                validated_ingredients.append(Ingredient(
                    name=ingredient_name,
                    amount=amount,
                    unit=unit,
                    cost_per_unit=standard_ing['avg_cost_per_unit'],
                    calories_per_unit=standard_ing['calories_per_100g']/100,  # per gram/ml
                    protein_per_unit=standard_ing['protein_per_100g']/100,
                    carbs_per_unit=standard_ing['carbs_per_100g']/100,
                    fat_per_unit=standard_ing['fat_per_100g']/100
                ))
            else:
                print(f"Warning: Ingredient '{ingredient_name}' not found in database. Skipping.")
                # Skip invalid ingredients
                continue
        
        # Calculate total nutritional values
        total_calories = sum(ing.calories_per_unit * ing.amount for ing in validated_ingredients)
        total_protein = sum(ing.protein_per_unit * ing.amount for ing in validated_ingredients)
        total_carbs = sum(ing.carbs_per_unit * ing.amount for ing in validated_ingredients)
        total_fat = sum(ing.fat_per_unit * ing.amount for ing in validated_ingredients)
        
        # Calculate total cost
        total_cost = sum(ing.cost_per_unit * ing.amount for ing in validated_ingredients)
        
        # Create the recipe object
        recipe = Recipe(
            id=self._generate_recipe_id(),
            name=recipe_data.get('name', 'Unnamed Recipe'),
            description=recipe_data.get('description', ''),
            ingredients=validated_ingredients,
            steps=recipe_data.get('steps', []),
            cooking_time_min=recipe_data.get('cooking_time_min', 30),
            difficulty_level=recipe_data.get('difficulty_level', 'intermediate'),
            cuisine_type=recipe_data.get('cuisine_type', 'various'),
            dietary_restrictions=recipe_data.get('dietary_restrictions', []),
            allergens=recipe_data.get('allergens', []),
            total_calories=total_calories,
            total_protein_g=total_protein,
            total_carbs_g=total_carbs,
            total_fat_g=total_fat,
            total_cost=total_cost
        )
        
        return recipe
    
    def _get_ingredient_from_db(self, ingredient_name: str) -> Dict:
        """
        Retrieve ingredient data from our database
        """
        # Load ingredients from JSON file
        ingredients_file = os.path.join(os.path.dirname(__file__), "../data/ingredients.json")
        
        try:
            with open(ingredients_file, 'r') as f:
                ingredients = json.load(f)
            
            # Find the ingredient
            for ing in ingredients:
                if normalize_ingredient_name(ing['name']) == normalize_ingredient_name(ingredient_name):
                    return ing
        except FileNotFoundError:
            print(f"Ingredients file not found at {ingredients_file}")
        except json.JSONDecodeError:
            print(f"Error decoding ingredients JSON from {ingredients_file}")
        
        # Return a default ingredient if not found
        return {
            "name": ingredient_name,
            "category": "unknown",
            "unit": "g",
            "avg_cost_per_unit": 0.1,
            "calories_per_100g": 100,
            "protein_per_100g": 5,
            "carbs_per_100g": 10,
            "fat_per_100g": 5,
            "allergens": [],
            "storage_days": 7
        }
    
    def _generate_recipe_id(self) -> str:
        """
        Generate a unique recipe ID
        """
        import uuid
        return str(uuid.uuid4())
    
    def _create_mock_recipe(
        self,
        dish_name: str,
        dietary_restrictions: List[str],
        allergens: List[str],
        cuisine_type: str,
        cooking_time: int
    ) -> Recipe:
        """
        Create a mock recipe for demonstration when OpenAI API is not available
        """
        # For demo purposes, return a simple recipe
        ingredients = [
            Ingredient(
                name="Salt",
                amount=5,
                unit="g",
                cost_per_unit=0.01,
                calories_per_unit=0,
                protein_per_unit=0,
                carbs_per_unit=0,
                fat_per_unit=0
            ),
            Ingredient(
                name="Pepper",
                amount=2,
                unit="g",
                cost_per_unit=0.05,
                calories_per_unit=2.5,
                protein_per_unit=0.1,
                carbs_per_unit=0.6,
                fat_per_unit=0.04
            )
        ]
        
        total_calories = sum(ing.calories_per_unit * ing.amount for ing in ingredients)
        total_protein = sum(ing.protein_per_unit * ing.amount for ing in ingredients)
        total_carbs = sum(ing.carbs_per_unit * ing.amount for ing in ingredients)
        total_fat = sum(ing.fat_per_unit * ing.amount for ing in ingredients)
        total_cost = sum(ing.cost_per_unit * ing.amount for ing in ingredients)
        
        return Recipe(
            id=self._generate_recipe_id(),
            name=dish_name,
            description=f"A delicious {cuisine_type} {dish_name}",
            ingredients=ingredients,
            steps=["Follow standard preparation for this dish."],
            cooking_time_min=min(cooking_time, 60),
            difficulty_level="beginner",
            cuisine_type=cuisine_type or "various",
            dietary_restrictions=dietary_restrictions,
            allergens=allergens,
            total_calories=total_calories,
            total_protein_g=total_protein,
            total_carbs_g=total_carbs,
            total_fat_g=total_fat,
            total_cost=total_cost
        )