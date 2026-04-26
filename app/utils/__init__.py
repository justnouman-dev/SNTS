"""
Utilities Package Initializer
"""
from .health_calculator import (
    calculate_bmi, 
    get_bmi_category, 
    suggest_diet_type,
    calculate_bmr,
    calculate_tdee,
    calculate_diet_targets,
    calculate_water_intake,
    calculate_macros_from_quantity
)
from .food_database import search_food, get_food_nutrition, get_all_foods
from .gamification import (
    calculate_daily_points,
    check_streak,
    get_badge_for_streak,
    get_badge_for_points,
    get_reward_options
)

__all__ = [
    'calculate_bmi',
    'get_bmi_category',
    'suggest_diet_type',
    'calculate_bmr',
    'calculate_tdee',
    'calculate_diet_targets',
    'calculate_water_intake',
    'calculate_macros_from_quantity',
    'search_food',
    'get_food_nutrition',
    'get_all_foods',
    'calculate_daily_points',
    'check_streak',
    'get_badge_for_streak',
    'get_badge_for_points',
    'get_reward_options'
]
