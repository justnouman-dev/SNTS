"""
Dashboard Routes
Main application dashboard and overview
"""
from flask import Blueprint, render_template, session, redirect, url_for, jsonify
from app.models import db, User, HealthSuggestion, FoodLog, HydrationLog, Reward
from app.routes.auth import login_required
from sqlalchemy import func
from datetime import date, timedelta

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')


@dashboard_bp.route('/api/dashboard-data')
@login_required
def get_dashboard_data():
    """Get dashboard summary data"""
    user_id = session['user_id']
    today = date.today()
    
    # Get user info
    user = User.query.get(user_id)
    
    # Get active health suggestion
    health_suggestion = HealthSuggestion.query.filter_by(
        user_id=user_id, 
        is_active=True
    ).order_by(HealthSuggestion.created_at.desc()).first()
    
    # Get today's food logs
    today_foods = FoodLog.query.filter_by(
        user_id=user_id,
        log_date=today
    ).all()
    
    # Calculate today's totals
    today_totals = {
        'calories': sum(log.total_calories for log in today_foods),
        'protein': sum(log.total_protein for log in today_foods),
        'carbs': sum(log.total_carbs for log in today_foods),
        'fats': sum(log.total_fats for log in today_foods)
    }
    
    # Get today's hydration
    hydration = HydrationLog.query.filter_by(
        user_id=user_id,
        log_date=today
    ).first()
    
    # Get reward data
    reward = Reward.query.filter_by(user_id=user_id).first()
    
    # Get weekly summary (last 7 days)
    week_ago = today - timedelta(days=7)
    weekly_logs = FoodLog.query.filter(
        FoodLog.user_id == user_id,
        FoodLog.log_date >= week_ago,
        FoodLog.log_date <= today
    ).all()
    
    weekly_calories = {}
    for log in weekly_logs:
        date_str = log.log_date.strftime('%Y-%m-%d')
        if date_str not in weekly_calories:
            weekly_calories[date_str] = 0
        weekly_calories[date_str] += log.total_calories
    
    return jsonify({
        'success': True,
        'user': {
            'username': user.username,
            'weight': user.weight,
            'height': user.height,
            'age': user.age,
            'gender': user.gender
        },
        'health_suggestion': {
            'bmi': health_suggestion.bmi if health_suggestion else 0,
            'bmi_category': health_suggestion.bmi_category if health_suggestion else 'N/A',
            'diet_type': health_suggestion.chosen_diet if health_suggestion else 'N/A',
            'targets': {
                'calories': health_suggestion.calorie_target if health_suggestion else 0,
                'protein': health_suggestion.protein_target if health_suggestion else 0,
                'carbs': health_suggestion.carbs_target if health_suggestion else 0,
                'fats': health_suggestion.fats_target if health_suggestion else 0
            }
        } if health_suggestion else None,
        'today_totals': today_totals,
        'hydration': {
            'current': hydration.water_intake if hydration else 0,
            'target': hydration.target_intake if hydration else user.weight * 35
        },
        'reward': {
            'points': reward.total_points if reward else 0,
            'streak': reward.current_streak if reward else 0,
            'badges': reward.badges.split(',') if reward and reward.badges else []
        },
        'weekly_data': weekly_calories
    })
