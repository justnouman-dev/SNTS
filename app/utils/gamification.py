"""
Gamification Utilities
Points, Streaks, and Rewards System
"""
from datetime import date, timedelta

def calculate_daily_points(food_logs_count, hydration_achieved):
    """
    Calculate points for daily activity
    - 10 points per food log entry
    - 50 bonus points if hydration goal achieved
    """
    points = food_logs_count * 10
    if hydration_achieved:
        points += 50
    return points


def check_streak(last_log_date):
    """
    Check if streak should continue or reset
    Returns: (is_streak_active, days_since_last_log)
    """
    if not last_log_date:
        return False, 0
    
    today = date.today()
    yesterday = today - timedelta(days=1)
    days_since = (today - last_log_date).days
    
    # Streak continues if logged yesterday or today
    if last_log_date in [today, yesterday]:
        return True, days_since
    else:
        return False, days_since


def get_badge_for_streak(streak):
    """
    Award badges based on streak milestones
    """
    badges = []
    if streak >= 7:
        badges.append("7-Day Warrior")
    if streak >= 30:
        badges.append("Monthly Champion")
    if streak >= 100:
        badges.append("Centurion")
    return badges


def get_badge_for_points(total_points):
    """
    Award badges based on total points
    """
    badges = []
    if total_points >= 100:
        badges.append("Beginner")
    if total_points >= 500:
        badges.append("Enthusiast")
    if total_points >= 1000:
        badges.append("Expert")
    if total_points >= 5000:
        badges.append("Master")
    return badges


def get_reward_options(total_points):
    """
    Get available rewards based on points
    """
    rewards = []
    
    if total_points >= 100:
        rewards.append({"name": "Health Tips", "cost": 100, "icon": "📚"})
    if total_points >= 250:
        rewards.append({"name": "Custom Diet Plan", "cost": 250, "icon": "🎯"})
    if total_points >= 500:
        rewards.append({"name": "Workout Guide", "cost": 500, "icon": "💪"})
    if total_points >= 1000:
        rewards.append({"name": "Nutrition Consultation", "cost": 1000, "icon": "👨‍⚕️"})
    
    return rewards
