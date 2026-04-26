"""
Health Calculation Utilities
BMI Calculator and Diet Recommendations
"""
import math

def calculate_bmi(weight, height):
    """
    Calculate BMI
    weight: kg
    height: cm
    """
    height_m = height / 100
    bmi = weight / (height_m ** 2)
    return round(bmi, 2)


def get_bmi_category(bmi):
    """Get BMI category"""
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 25:
        return "Normal Weight"
    elif 25 <= bmi < 30:
        return "Overweight"
    else:
        return "Obese"


def suggest_diet_type(bmi, bmi_category):
    """
    Suggest diet type based on BMI
    """
    if bmi_category == "Underweight":
        return "Bulking"
    elif bmi_category == "Normal Weight":
        return "Maintenance"
    elif bmi_category in ["Overweight", "Obese"]:
        return "Cutting"
    return "Maintenance"


def calculate_bmr(weight, height, age, gender):
    """
    Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation
    weight: kg
    height: cm
    age: years
    gender: Male/Female
    """
    if gender.lower() == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    return round(bmr, 2)


def calculate_tdee(bmr, activity_level="moderate"):
    """
    Calculate Total Daily Energy Expenditure
    activity_level: sedentary, light, moderate, active, very_active
    """
    activity_multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9
    }
    multiplier = activity_multipliers.get(activity_level, 1.55)
    return round(bmr * multiplier, 2)


def calculate_diet_targets(weight, height, age, gender, diet_type):
    """
    Calculate daily nutrition targets based on diet type
    """
    bmr = calculate_bmr(weight, height, age, gender)
    tdee = calculate_tdee(bmr, "moderate")
    
    if diet_type == "Bulking":
        # Surplus of 300-500 calories
        calorie_target = int(tdee + 400)
        protein_target = int(weight * 2.0)  # 2g per kg
        fats_target = int(weight * 1.0)  # 1g per kg
        # Remaining from carbs (4 cal/g for protein and carbs, 9 cal/g for fats)
        carbs_target = int((calorie_target - (protein_target * 4) - (fats_target * 9)) / 4)
        
    elif diet_type == "Cutting":
        # Deficit of 300-500 calories
        calorie_target = int(tdee - 400)
        protein_target = int(weight * 2.2)  # Higher protein to preserve muscle
        fats_target = int(weight * 0.8)  # Slightly lower fats
        carbs_target = int((calorie_target - (protein_target * 4) - (fats_target * 9)) / 4)
        
    else:  # Maintenance
        calorie_target = int(tdee)
        protein_target = int(weight * 1.8)
        fats_target = int(weight * 0.9)
        carbs_target = int((calorie_target - (protein_target * 4) - (fats_target * 9)) / 4)
    
    return {
        'calorie_target': calorie_target,
        'protein_target': protein_target,
        'carbs_target': carbs_target,
        'fats_target': fats_target
    }


def calculate_water_intake(weight):
    """
    Calculate recommended daily water intake
    weight: kg
    Returns: ml
    """
    # Standard formula: 30-35 ml per kg body weight
    water_ml = weight * 35
    return round(water_ml, 2)


def calculate_macros_from_quantity(calories_per_100g, protein_per_100g, carbs_per_100g, fats_per_100g, quantity):
    """
    Calculate total macros based on quantity consumed
    All per_100g values are for 100g
    quantity: grams consumed
    """
    multiplier = quantity / 100
    return {
        'total_calories': round(calories_per_100g * multiplier, 2),
        'total_protein': round(protein_per_100g * multiplier, 2),
        'total_carbs': round(carbs_per_100g * multiplier, 2),
        'total_fats': round(fats_per_100g * multiplier, 2)
    }
