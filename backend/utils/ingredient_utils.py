"""
Utility functions for ingredient normalization and processing
"""

# Mapping of common ingredient variations to standard names
INGREDIENT_VARIATIONS = {
    "bell pepper": ["bell pepper", "red pepper", "capsicum", "pepper"],
    "chicken breast": ["chicken breast", "chicken", "chicken fillet"],
    "broccoli": ["broccoli", "brocolli"],
    "spinach": ["spinach", "spinage"],
    "rice": ["rice", "white rice", "long grain rice"],
    "quinoa": ["quinoa", "quinoia"],
    "olive oil": ["olive oil", "extra virgin olive oil", "evoo"],
    "tofu": ["tofu", "bean curd"],
    "salmon": ["salmon", "salmon fillet"],
    "avocado": ["avocado", "avacado"],
    "banana": ["banana", "bananas"],
    "almonds": ["almonds", "almond"],
}

# Reverse mapping for quick lookup
VARIATION_TO_STANDARD = {}
for standard, variations in INGREDIENT_VARIATIONS.items():
    for variation in variations:
        VARIATION_TO_STANDARD[variation.lower()] = standard


def normalize_ingredient_name(name: str) -> str:
    """
    Normalize ingredient name to standard form
    """
    name_lower = name.lower().strip()
    return VARIATION_TO_STANDARD.get(name_lower, name_lower)


def get_standard_ingredient_names() -> list:
    """
    Get list of all standard ingredient names
    """
    return list(INGREDIENT_VARIATIONS.keys())


def is_valid_ingredient(name: str) -> bool:
    """
    Check if an ingredient name is valid (exists in our database)
    """
    return normalize_ingredient_name(name) in get_standard_ingredient_names()


# Unit conversion mappings
UNIT_CONVERSIONS = {
    # Weight
    "kg": {"g": 1000},
    "g": {"kg": 0.001, "mg": 1000},
    "mg": {"g": 0.001},
    
    # Volume
    "l": {"ml": 1000},
    "ml": {"l": 0.001},
    
    # Imperial to metric
    "cup": {"ml": 240, "g": 240},  # Approximate for water-like density
    "tbsp": {"ml": 15, "g": 15},
    "tsp": {"ml": 5, "g": 5},
    "oz": {"g": 28.35},
    "lb": {"g": 453.592},
}


def convert_units(amount: float, from_unit: str, to_unit: str) -> float:
    """
    Convert amount from one unit to another
    """
    if from_unit == to_unit:
        return amount
    
    conversions = UNIT_CONVERSIONS.get(from_unit, {})
    factor = conversions.get(to_unit)
    
    if factor is not None:
        return amount * factor
    else:
        raise ValueError(f"Cannot convert from {from_unit} to {to_unit}")


def standardize_units(ingredient_name: str, amount: float, unit: str) -> tuple:
    """
    Standardize ingredient units to a consistent format
    """
    # For now, we'll convert everything to grams or ml as appropriate
    # This would be expanded based on the ingredient type
    standard_unit = unit
    standard_amount = amount
    
    # Simple heuristics for standardization
    if unit in ["kg", "mg", "lb", "oz"]:
        if unit == "kg":
            standard_amount = amount * 1000
            standard_unit = "g"
        elif unit == "mg":
            standard_amount = amount / 1000
            standard_unit = "g"
        elif unit == "lb":
            standard_amount = amount * 453.592
            standard_unit = "g"
        elif unit == "oz":
            standard_amount = amount * 28.35
            standard_unit = "g"
    elif unit in ["l", "tbsp", "tsp", "cup"]:
        if unit == "l":
            standard_amount = amount * 1000
            standard_unit = "ml"
        elif unit == "cup":
            standard_amount = amount * 240
            standard_unit = "ml"
        elif unit == "tbsp":
            standard_amount = amount * 15
            standard_unit = "ml"
        elif unit == "tsp":
            standard_amount = amount * 5
            standard_unit = "ml"
    
    return standard_amount, standard_unit