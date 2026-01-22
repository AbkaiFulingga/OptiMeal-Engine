from typing import Dict, List, Tuple
from models.recipe import Recipe
from models.user_preferences import UserPreferences
import json
import os


class GroceryOptimizerService:
    def __init__(self, prices_file_path: str = "../data/prices.json"):
        """
        Initialize the grocery optimizer service with store price data
        """
        self.prices_file_path = os.path.join(os.path.dirname(__file__), prices_file_path)
        self._price_database = self._load_price_data()
    
    def _load_price_data(self) -> Dict:
        """
        Load price data from file or create default if not exists
        """
        if not os.path.exists(self.prices_file_path):
            self._create_default_prices()
        
        try:
            with open(self.prices_file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Prices file not found at {self.prices_file_path}")
            return {}
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {self.prices_file_path}")
            return {}
    
    def _create_default_prices(self):
        """
        Create a default price database if it doesn't exist
        """
        default_prices = {
            "stores": [
                {
                    "id": "store_1",
                    "name": "FreshMart",
                    "location": "Downtown"
                },
                {
                    "id": "store_2", 
                    "name": "ValueGrocer",
                    "location": "Uptown"
                },
                {
                    "id": "store_3",
                    "name": "Organic Plus",
                    "location": "Midtown"
                }
            ],
            "prices": [
                {
                    "ingredient": "Chicken Breast",
                    "store_id": "store_1",
                    "unit": "g",
                    "price_per_unit": 0.11,
                    "section": "meat"
                },
                {
                    "ingredient": "Chicken Breast", 
                    "store_id": "store_2",
                    "unit": "g",
                    "price_per_unit": 0.13,
                    "section": "meat"
                },
                {
                    "ingredient": "Chicken Breast",
                    "store_id": "store_3",
                    "unit": "g", 
                    "price_per_unit": 0.15,
                    "section": "meat"
                },
                {
                    "ingredient": "Broccoli",
                    "store_id": "store_1",
                    "unit": "g",
                    "price_per_unit": 0.012,
                    "section": "produce"
                },
                {
                    "ingredient": "Broccoli",
                    "store_id": "store_2",
                    "unit": "g",
                    "price_per_unit": 0.009,
                    "section": "produce"
                },
                {
                    "ingredient": "Broccoli",
                    "store_id": "store_3",
                    "unit": "g",
                    "price_per_unit": 0.015,
                    "section": "produce"
                },
                {
                    "ingredient": "Rice",
                    "store_id": "store_1",
                    "unit": "g",
                    "price_per_unit": 0.018,
                    "section": "pantry"
                },
                {
                    "ingredient": "Rice",
                    "store_id": "store_2",
                    "unit": "g",
                    "price_per_unit": 0.022,
                    "section": "pantry"
                },
                {
                    "ingredient": "Rice",
                    "store_id": "store_3",
                    "unit": "g",
                    "price_per_unit": 0.020,
                    "section": "pantry"
                }
            ]
        }
        
        # Create the data directory if it doesn't exist
        os.makedirs(os.path.dirname(self.prices_file_path), exist_ok=True)
        
        with open(self.prices_file_path, 'w') as f:
            json.dump(default_prices, f, indent=2)
    
    def optimize_grocery_list(
        self,
        grocery_list: Dict[str, float],
        user_preferences: UserPreferences,
        single_store_mode: bool = True
    ) -> Dict:
        """
        Optimize the grocery list by selecting the best store for each ingredient
        and grouping by store sections
        """
        optimized_list = {
            "single_store_mode": single_store_mode,
            "selected_store": None,
            "stores_used": [],
            "total_cost": 0,
            "items_by_store": {},
            "items_by_section": {},  # For a single store
            "substitutions": [],  # Potential cheaper alternatives
            "cost_savings": 0  # Potential savings from optimizations
        }
        
        if single_store_mode:
            # Find the single best store for all items
            best_store = self._find_best_single_store(grocery_list)
            optimized_list["selected_store"] = best_store
            optimized_list["stores_used"] = [best_store]
            
            # Calculate optimized list for the selected store
            store_items, total_cost = self._calculate_store_items(grocery_list, best_store["id"])
            optimized_list["items_by_store"] = {best_store["id"]: store_items}
            optimized_list["total_cost"] = total_cost
            
            # Group by section for the selected store
            optimized_list["items_by_section"] = self._group_by_section(store_items)
        else:
            # Multi-store mode: select best store for each ingredient
            optimized_list["items_by_store"], total_cost = self._optimize_multi_store(grocery_list)
            optimized_list["total_cost"] = total_cost
            optimized_list["stores_used"] = list(optimized_list["items_by_store"].keys())
        
        # Find potential substitutions
        optimized_list["substitutions"] = self._find_substitutions(grocery_list)
        
        return optimized_list
    
    def _find_best_single_store(self, grocery_list: Dict[str, float]) -> Dict:
        """
        Find the store that offers the lowest total cost for all required items
        """
        if not self._price_database:
            # If no price data, return a default store
            return {"id": "default", "name": "Default Store", "location": "N/A"}
        
        stores = self._price_database.get("stores", [])
        if not stores:
            return {"id": "default", "name": "Default Store", "location": "N/A"}
        
        best_store = None
        lowest_total_cost = float('inf')
        
        for store in stores:
            total_cost = 0
            can_supply_all = True
            
            for item_name, quantity in grocery_list.items():
                # Extract ingredient name from "ingredient (unit)" format
                ingredient_name = item_name.split(' (')[0]
                
                price_info = self._find_lowest_price_for_ingredient_in_store(ingredient_name, store["id"])
                if price_info:
                    total_cost += price_info["price_per_unit"] * quantity
                else:
                    # Cannot supply this item from this store
                    can_supply_all = False
                    break
            
            if can_supply_all and total_cost < lowest_total_cost:
                lowest_total_cost = total_cost
                best_store = store
        
        # If no store can supply all items, return the first store as fallback
        if best_store is None:
            best_store = stores[0]
        
        return best_store
    
    def _find_lowest_price_for_ingredient_in_store(self, ingredient: str, store_id: str) -> Dict:
        """
        Find the price info for an ingredient in a specific store
        """
        prices = self._price_database.get("prices", [])
        
        for price_entry in prices:
            if (price_entry["ingredient"].lower() == ingredient.lower() and 
                price_entry["store_id"] == store_id):
                return price_entry
        
        return None
    
    def _calculate_store_items(self, grocery_list: Dict[str, float], store_id: str) -> Tuple[List, float]:
        """
        Calculate items and total cost for a specific store
        """
        items = []
        total_cost = 0
        
        for item_name, quantity in grocery_list.items():
            # Extract ingredient name from "ingredient (unit)" format
            ingredient_name = item_name.split(' (')[0]
            
            price_info = self._find_lowest_price_for_ingredient_in_store(ingredient_name, store_id)
            if price_info:
                item_cost = price_info["price_per_unit"] * quantity
                total_cost += item_cost
                
                items.append({
                    "name": ingredient_name,
                    "quantity": quantity,
                    "unit": price_info["unit"],
                    "unit_price": price_info["price_per_unit"],
                    "total_price": item_cost,
                    "section": price_info["section"]
                })
            else:
                # If ingredient not available in this store, use default price
                # This would come from the recipe ingredient data
                items.append({
                    "name": ingredient_name,
                    "quantity": quantity,
                    "unit": "g",  # Default unit
                    "unit_price": 0.10,  # Default price
                    "total_price": 0.10 * quantity,
                    "section": "unknown"
                })
                total_cost += 0.10 * quantity
        
        return items, total_cost
    
    def _group_by_section(self, items: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Group items by store section
        """
        grouped = {}
        for item in items:
            section = item.get("section", "miscellaneous")
            if section not in grouped:
                grouped[section] = []
            grouped[section].append(item)
        return grouped
    
    def _optimize_multi_store(self, grocery_list: Dict[str, float]) -> Tuple[Dict, float]:
        """
        Optimize for multi-store mode by selecting the best store for each ingredient
        """
        items_by_store = {}
        total_cost = 0
        
        for item_name, quantity in grocery_list.items():
            # Extract ingredient name from "ingredient (unit)" format
            ingredient_name = item_name.split(' (')[0]
            
            # Find the store with the lowest price for this ingredient
            best_price_info = self._find_lowest_price_for_ingredient(ingredient_name)
            
            if best_price_info:
                store_id = best_price_info["store_id"]
                if store_id not in items_by_store:
                    items_by_store[store_id] = []
                
                item_cost = best_price_info["price_per_unit"] * quantity
                total_cost += item_cost
                
                item_details = {
                    "name": ingredient_name,
                    "quantity": quantity,
                    "unit": best_price_info["unit"],
                    "unit_price": best_price_info["price_per_unit"],
                    "total_price": item_cost,
                    "section": best_price_info["section"]
                }
                
                items_by_store[store_id].append(item_details)
            else:
                # If no price found, add to first store as fallback
                if not items_by_store:
                    # Create a default store entry
                    items_by_store["default"] = []
                
                store_id = list(items_by_store.keys())[0]
                item_cost = 0.10 * quantity  # Default cost
                total_cost += item_cost
                
                item_details = {
                    "name": ingredient_name,
                    "quantity": quantity,
                    "unit": "g",
                    "unit_price": 0.10,
                    "total_price": item_cost,
                    "section": "unknown"
                }
                
                items_by_store[store_id].append(item_details)
        
        return items_by_store, total_cost
    
    def _find_lowest_price_for_ingredient(self, ingredient: str) -> Dict:
        """
        Find the store with the lowest price for an ingredient across all stores
        """
        prices = self._price_database.get("prices", [])
        lowest_price = None
        lowest_price_info = None
        
        for price_entry in prices:
            if price_entry["ingredient"].lower() == ingredient.lower():
                if lowest_price is None or price_entry["price_per_unit"] < lowest_price:
                    lowest_price = price_entry["price_per_unit"]
                    lowest_price_info = price_entry
        
        return lowest_price_info
    
    def _find_substitutions(self, grocery_list: Dict[str, float]) -> List[Dict]:
        """
        Find potential cheaper substitutions for ingredients
        """
        substitutions = []
        
        for item_name, quantity in grocery_list.items():
            ingredient_name = item_name.split(' (')[0]
            
            # Find alternative options for this ingredient
            all_prices = self._find_all_prices_for_ingredient(ingredient_name)
            
            if len(all_prices) > 1:
                # Sort by price to find cheaper alternatives
                all_prices.sort(key=lambda x: x["price_per_unit"])
                
                # If the cheapest option is significantly cheaper, suggest it
                current_price = all_prices[0]["price_per_unit"]
                if len(all_prices) > 1:
                    next_cheapest = all_prices[1]["price_per_unit"]
                    if next_cheapest < current_price * 0.9:  # More than 10% cheaper
                        substitutions.append({
                            "original_item": ingredient_name,
                            "alternative_store": self._get_store_name(all_prices[1]["store_id"]),
                            "original_price": current_price,
                            "alternative_price": next_cheapest,
                            "savings_per_unit": current_price - next_cheapest,
                            "estimated_savings": (current_price - next_cheapest) * quantity
                        })
        
        return substitutions
    
    def _find_all_prices_for_ingredient(self, ingredient: str) -> List[Dict]:
        """
        Find all price options for an ingredient across all stores
        """
        prices = self._price_database.get("prices", [])
        matches = []
        
        for price_entry in prices:
            if price_entry["ingredient"].lower() == ingredient.lower():
                matches.append(price_entry)
        
        return matches
    
    def _get_store_name(self, store_id: str) -> str:
        """
        Get the name of a store by its ID
        """
        stores = self._price_database.get("stores", [])
        for store in stores:
            if store["id"] == store_id:
                return store["name"]
        return "Unknown Store"