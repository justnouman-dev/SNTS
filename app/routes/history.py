"""
History & Analytics Routes
View historical data and analytics
"""
from flask import Blueprint, render_template, request, jsonify, session
from app.models import db, FoodLog, HydrationLog, HealthSuggestion
from app.routes.auth import login_required
from sqlalchemy import func
from datetime import date, timedelta

history_bp = Blueprint('history', __name__)


@history_bp.route('/history')
@login_required
def history():
    """History page"""
    return render_template('history.html')


@history_bp.route('/api/food-history')
@login_required
def food_history():
    """Get food log history with pagination"""
    user_id = session['user_id']
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Get date filter if provided
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = FoodLog.query.filter_by(user_id=user_id)
    
    if start_date:
        query = query.filter(FoodLog.log_date >= start_date)
    if end_date:
        query = query.filter(FoodLog.log_date <= end_date)
    
    logs = query.order_by(FoodLog.log_date.desc(), FoodLog.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'success': True,
        'logs': [{
            'id': log.id,
            'food_name': log.food_name,
            'quantity': log.quantity,
            'total_calories': log.total_calories,
            'total_protein': log.total_protein,
            'total_carbs': log.total_carbs,
            'total_fats': log.total_fats,
            'date': log.log_date.strftime('%Y-%m-%d'),
            'time': log.created_at.strftime('%H:%M')
        } for log in logs.items],
        'pagination': {
            'page': logs.page,
            'pages': logs.pages,
            'total': logs.total,
            'has_next': logs.has_next,
            'has_prev': logs.has_prev
        }
    })


@history_bp.route('/api/daily-summary')
@login_required
def daily_summary():
    """Get daily nutrition summary for date range"""
    user_id = session['user_id']
    days = request.args.get('days', 7, type=int)
    
    end_date = date.today()
    start_date = end_date - timedelta(days=days-1)
    
    # Get all logs in date range
    logs = FoodLog.query.filter(
        FoodLog.user_id == user_id,
        FoodLog.log_date >= start_date,
        FoodLog.log_date <= end_date
    ).all()
    
    # Group by date
    daily_data = {}
    for log in logs:
        date_str = log.log_date.strftime('%Y-%m-%d')
        if date_str not in daily_data:
            daily_data[date_str] = {
                'date': date_str,
                'calories': 0,
                'protein': 0,
                'carbs': 0,
                'fats': 0,
                'logs_count': 0
            }
        daily_data[date_str]['calories'] += log.total_calories
        daily_data[date_str]['protein'] += log.total_protein
        daily_data[date_str]['carbs'] += log.total_carbs
        daily_data[date_str]['fats'] += log.total_fats
        daily_data[date_str]['logs_count'] += 1
    
    # Fill in missing dates with zeros
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        if date_str not in daily_data:
            daily_data[date_str] = {
                'date': date_str,
                'calories': 0,
                'protein': 0,
                'carbs': 0,
                'fats': 0,
                'logs_count': 0
            }
        current_date += timedelta(days=1)
    
    # Sort by date
    sorted_data = sorted(daily_data.values(), key=lambda x: x['date'])
    
    return jsonify({
        'success': True,
        'daily_data': sorted_data
    })


@history_bp.route('/api/nutrition-trends')
@login_required
def nutrition_trends():
    """Get nutrition trends and averages"""
    user_id = session['user_id']
    days = request.args.get('days', 30, type=int)
    
    end_date = date.today()
    start_date = end_date - timedelta(days=days-1)
    
    # Get all logs in date range
    logs = FoodLog.query.filter(
        FoodLog.user_id == user_id,
        FoodLog.log_date >= start_date,
        FoodLog.log_date <= end_date
    ).all()
    
    if not logs:
        return jsonify({
            'success': True,
            'averages': {'calories': 0, 'protein': 0, 'carbs': 0, 'fats': 0},
            'totals': {'calories': 0, 'protein': 0, 'carbs': 0, 'fats': 0},
            'days_logged': 0
        })
    
    # Calculate totals
    totals = {
        'calories': sum(log.total_calories for log in logs),
        'protein': sum(log.total_protein for log in logs),
        'carbs': sum(log.total_carbs for log in logs),
        'fats': sum(log.total_fats for log in logs)
    }
    
    # Get unique days logged
    unique_days = len(set(log.log_date for log in logs))
    
    # Calculate averages
    averages = {
        'calories': round(totals['calories'] / unique_days, 1),
        'protein': round(totals['protein'] / unique_days, 1),
        'carbs': round(totals['carbs'] / unique_days, 1),
        'fats': round(totals['fats'] / unique_days, 1)
    }
    
    return jsonify({
        'success': True,
        'averages': averages,
        'totals': totals,
        'days_logged': unique_days,
        'total_days': days
    })


@history_bp.route('/api/hydration-history')
@login_required
def hydration_history():
    """Get hydration history"""
    user_id = session['user_id']
    days = request.args.get('days', 7, type=int)
    
    end_date = date.today()
    start_date = end_date - timedelta(days=days-1)
    
    logs = HydrationLog.query.filter(
        HydrationLog.user_id == user_id,
        HydrationLog.log_date >= start_date,
        HydrationLog.log_date <= end_date
    ).order_by(HydrationLog.log_date.desc()).all()
    
    return jsonify({
        'success': True,
        'hydration_data': [{
            'date': log.log_date.strftime('%Y-%m-%d'),
            'intake': log.water_intake,
            'target': log.target_intake,
            'percentage': round((log.water_intake / log.target_intake) * 100, 1)
        } for log in logs]
    })


@history_bp.route('/api/suggestion-history')
@login_required
def suggestion_history():
    """Get health suggestion history"""
    user_id = session['user_id']
    
    suggestions = HealthSuggestion.query.filter_by(
        user_id=user_id
    ).order_by(HealthSuggestion.created_at.desc()).limit(10).all()
    
    return jsonify({
        'success': True,
        'suggestions': [{
            'id': s.id,
            'bmi': s.bmi,
            'bmi_category': s.bmi_category,
            'suggested_diet': s.suggested_diet,
            'chosen_diet': s.chosen_diet,
            'targets': {
                'calories': s.calorie_target,
                'protein': s.protein_target,
                'carbs': s.carbs_target,
                'fats': s.fats_target
            },
            'created_at': s.created_at.strftime('%Y-%m-%d %H:%M'),
            'is_active': s.is_active
        } for s in suggestions]
    })
