"""
Local Food Nutrition Database
Comprehensive Indian and International food items with nutritional values per 100g
"""

FOOD_DATABASE = {
    # Grains & Cereals
    "rice": {"calories": 130, "protein": 2.7, "carbs": 28.2, "fats": 0.3},
    "brown rice": {"calories": 111, "protein": 2.6, "carbs": 23, "fats": 0.9},
    "wheat flour": {"calories": 364, "protein": 10, "carbs": 76, "fats": 1.5},
    "oats": {"calories": 389, "protein": 16.9, "carbs": 66.3, "fats": 6.9},
    "quinoa": {"calories": 120, "protein": 4.4, "carbs": 21.3, "fats": 1.9},
    "bread": {"calories": 265, "protein": 9, "carbs": 49, "fats": 3.2},
    "white bread": {"calories": 265, "protein": 9, "carbs": 49, "fats": 3.2},
    "brown bread": {"calories": 247, "protein": 13, "carbs": 41, "fats": 3.4},
    "roti": {"calories": 297, "protein": 11, "carbs": 51, "fats": 6.7},
    "chapati": {"calories": 297, "protein": 11, "carbs": 51, "fats": 6.7},
    "paratha": {"calories": 320, "protein": 6, "carbs": 40, "fats": 15},
    
    # Proteins
    "chicken breast": {"calories": 165, "protein": 31, "carbs": 0, "fats": 3.6},
    "chicken": {"calories": 239, "protein": 27, "carbs": 0, "fats": 14},
    "egg": {"calories": 155, "protein": 13, "carbs": 1.1, "fats": 11},
    "boiled egg": {"calories": 155, "protein": 13, "carbs": 1.1, "fats": 11},
    "paneer": {"calories": 265, "protein": 18.3, "carbs": 3.4, "fats": 20.8},
    "tofu": {"calories": 76, "protein": 8, "carbs": 1.9, "fats": 4.8},
    "fish": {"calories": 206, "protein": 22, "carbs": 0, "fats": 12},
    "salmon": {"calories": 208, "protein": 20, "carbs": 0, "fats": 13},
    "tuna": {"calories": 130, "protein": 30, "carbs": 0, "fats": 0.95},
    "mutton": {"calories": 294, "protein": 25, "carbs": 0, "fats": 21},
    
    # Dairy
    "milk": {"calories": 61, "protein": 3.2, "carbs": 4.8, "fats": 3.3},
    "curd": {"calories": 61, "protein": 3.5, "carbs": 4.7, "fats": 3.3},
    "yogurt": {"calories": 59, "protein": 10, "carbs": 3.6, "fats": 0.4},
    "cheese": {"calories": 402, "protein": 25, "carbs": 1.3, "fats": 33},
    "butter": {"calories": 717, "protein": 0.9, "carbs": 0.1, "fats": 81},
    "ghee": {"calories": 900, "protein": 0, "carbs": 0, "fats": 100},
    
    # Legumes & Pulses
    "dal": {"calories": 116, "protein": 9, "carbs": 20, "fats": 0.5},
    "moong dal": {"calories": 347, "protein": 24, "carbs": 59, "fats": 1.2},
    "chana dal": {"calories": 378, "protein": 22.5, "carbs": 60, "fats": 5.6},
    "toor dal": {"calories": 335, "protein": 22, "carbs": 62, "fats": 1.5},
    "rajma": {"calories": 333, "protein": 23.6, "carbs": 60.6, "fats": 0.8},
    "chickpeas": {"calories": 364, "protein": 19, "carbs": 61, "fats": 6},
    "lentils": {"calories": 116, "protein": 9, "carbs": 20, "fats": 0.4},
    "kidney beans": {"calories": 333, "protein": 23.6, "carbs": 60.6, "fats": 0.8},
    
    # Vegetables
    "potato": {"calories": 77, "protein": 2, "carbs": 17, "fats": 0.1},
    "sweet potato": {"calories": 86, "protein": 1.6, "carbs": 20, "fats": 0.1},
    "tomato": {"calories": 18, "protein": 0.9, "carbs": 3.9, "fats": 0.2},
    "onion": {"calories": 40, "protein": 1.1, "carbs": 9.3, "fats": 0.1},
    "spinach": {"calories": 23, "protein": 2.9, "carbs": 3.6, "fats": 0.4},
    "broccoli": {"calories": 34, "protein": 2.8, "carbs": 7, "fats": 0.4},
    "carrot": {"calories": 41, "protein": 0.9, "carbs": 10, "fats": 0.2},
    "cucumber": {"calories": 16, "protein": 0.7, "carbs": 3.6, "fats": 0.1},
    "capsicum": {"calories": 20, "protein": 0.9, "carbs": 4.6, "fats": 0.2},
    "cauliflower": {"calories": 25, "protein": 1.9, "carbs": 5, "fats": 0.3},
    "cabbage": {"calories": 25, "protein": 1.3, "carbs": 5.8, "fats": 0.1},
    "peas": {"calories": 81, "protein": 5.4, "carbs": 14.5, "fats": 0.4},
    
    # Fruits
    "banana": {"calories": 89, "protein": 1.1, "carbs": 23, "fats": 0.3},
    "apple": {"calories": 52, "protein": 0.3, "carbs": 14, "fats": 0.2},
    "orange": {"calories": 47, "protein": 0.9, "carbs": 12, "fats": 0.1},
    "mango": {"calories": 60, "protein": 0.8, "carbs": 15, "fats": 0.4},
    "grapes": {"calories": 69, "protein": 0.7, "carbs": 18, "fats": 0.2},
    "watermelon": {"calories": 30, "protein": 0.6, "carbs": 7.5, "fats": 0.2},
    "papaya": {"calories": 43, "protein": 0.5, "carbs": 11, "fats": 0.3},
    "pomegranate": {"calories": 83, "protein": 1.7, "carbs": 19, "fats": 1.2},
    "strawberry": {"calories": 32, "protein": 0.7, "carbs": 7.7, "fats": 0.3},
    
    # Nuts & Seeds
    "almonds": {"calories": 579, "protein": 21, "carbs": 22, "fats": 50},
    "cashew": {"calories": 553, "protein": 18, "carbs": 30, "fats": 44},
    "peanuts": {"calories": 567, "protein": 26, "carbs": 16, "fats": 49},
    "walnuts": {"calories": 654, "protein": 15, "carbs": 14, "fats": 65},
    "chia seeds": {"calories": 486, "protein": 17, "carbs": 42, "fats": 31},
    "pumpkin seeds": {"calories": 446, "protein": 19, "carbs": 54, "fats": 19},
    
    # Fast Food / Snacks
    "pizza": {"calories": 266, "protein": 11, "carbs": 33, "fats": 10},
    "burger": {"calories": 295, "protein": 17, "carbs": 34, "fats": 10},
    "pasta": {"calories": 131, "protein": 5, "carbs": 25, "fats": 1.1},
    "french fries": {"calories": 312, "protein": 3.4, "carbs": 41, "fats": 15},
    "chips": {"calories": 536, "protein": 6.6, "carbs": 53, "fats": 34},
    "samosa": {"calories": 262, "protein": 5.4, "carbs": 25, "fats": 17},
    "pakora": {"calories": 240, "protein": 4, "carbs": 23, "fats": 15},
    
    # Beverages & Others
    "coffee": {"calories": 2, "protein": 0.3, "carbs": 0, "fats": 0},
    "tea": {"calories": 1, "protein": 0, "carbs": 0.3, "fats": 0},
    "coconut oil": {"calories": 884, "protein": 0, "carbs": 0, "fats": 100},
    "olive oil": {"calories": 884, "protein": 0, "carbs": 0, "fats": 100},
    "honey": {"calories": 304, "protein": 0.3, "carbs": 82, "fats": 0},
    "sugar": {"calories": 387, "protein": 0, "carbs": 100, "fats": 0},
    "dark chocolate": {"calories": 546, "protein": 4.9, "carbs": 61, "fats": 31},
}


def search_food(query):
    """
    Search for food in database
    Returns list of matching foods
    """
    query = query.lower().strip()
    results = []
    
    for food_name, nutrition in FOOD_DATABASE.items():
        if query in food_name:
            results.append({
                'name': food_name.title(),
                'nutrition': nutrition
            })
    
    return results


def get_food_nutrition(food_name):
    """
    Get nutrition info for specific food
    Returns None if not found
    """
    food_name = food_name.lower().strip()
    if food_name in FOOD_DATABASE:
        return FOOD_DATABASE[food_name]
    return None


def get_all_foods():
    """Get list of all available foods"""
    return sorted([food.title() for food in FOOD_DATABASE.keys()])
