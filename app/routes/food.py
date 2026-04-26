"""
Food Logging Routes
Smart food logging with nutrition tracking
"""
from flask import Blueprint, render_template, request, jsonify, session
from app.models import db, User, FoodLog, Reward, HealthSuggestion
from app.routes.auth import login_required
from app.utils import get_food_nutrition, search_food, get_all_foods, calculate_macros_from_quantity
from app.utils import calculate_daily_points, check_streak, get_badge_for_streak, get_badge_for_points
from datetime import date

food_bp = Blueprint('food', __name__)


@food_bp.route('/food-log')
@login_required
def food_log():
    """Food logging page"""
    return render_template('food_log.html')


@food_bp.route('/api/search-food')
@login_required
def search_food_api():
    """Search for food in database"""
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 2:
        return jsonify({'success': False, 'message': 'Query too short'}), 400
    
    results = search_food(query)
    
    return jsonify({
        'success': True,
        'results': results
    })


@food_bp.route('/api/all-foods')
@login_required
def all_foods():
    """Get list of all available foods"""
    foods = get_all_foods()
    return jsonify({
        'success': True,
        'foods': foods
    })


@food_bp.route('/api/log-food', methods=['POST'])
@login_required
def log_food():
    """Log food consumption"""
    user_id = session['user_id']
    data = request.get_json()
    
    food_name = data.get('food_name', '').strip()
    quantity = data.get('quantity')
    
    if not food_name or not quantity:
        return jsonify({'success': False, 'message': 'Food name and quantity required'}), 400
    
    try:
        quantity = float(quantity)
        if quantity <= 0:
            return jsonify({'success': False, 'message': 'Quantity must be positive'}), 400
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid quantity'}), 400
    
    # Get nutrition info
    nutrition = get_food_nutrition(food_name)
    
    if not nutrition:
        return jsonify({'success': False, 'message': 'Food not found in database'}), 404
    
    # Calculate totals based on quantity
    totals = calculate_macros_from_quantity(
        nutrition['calories'],
        nutrition['protein'],
        nutrition['carbs'],
        nutrition['fats'],
        quantity
    )
    
    # Create food log
    food_log = FoodLog(
        user_id=user_id,
        food_name=food_name.title(),
        quantity=quantity,
        calories=nutrition['calories'],
        protein=nutrition['protein'],
        carbs=nutrition['carbs'],
        fats=nutrition['fats'],
        total_calories=totals['total_calories'],
        total_protein=totals['total_protein'],
        total_carbs=totals['total_carbs'],
        total_fats=totals['total_fats'],
        log_date=date.today()
    )
    
    db.session.add(food_log)
    
    # Update rewards
    reward = Reward.query.filter_by(user_id=user_id).first()
    if reward:
        today = date.today()
        
        # Check streak
        is_active, days_since = check_streak(reward.last_log_date)
        
        if not is_active and days_since > 1:
            # Streak broken
            reward.current_streak = 1
        elif reward.last_log_date == today:
            # Already logged today, no streak change
            pass
        else:
            # Continue or start streak
            reward.current_streak += 1
            if reward.current_streak > reward.longest_streak:
                reward.longest_streak = reward.current_streak
        
        # Add points (10 per log)
        reward.total_points += 10
        reward.last_log_date = today
        
        # Check for new badges
        streak_badges = get_badge_for_streak(reward.current_streak)
        point_badges = get_badge_for_points(reward.total_points)
        all_badges = list(set(streak_badges + point_badges))
        reward.badges = ','.join(all_badges)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Food logged successfully',
        'log': {
            'id': food_log.id,
            'food_name': food_log.food_name,
            'quantity': food_log.quantity,
            'totals': totals
        },
        'reward_update': {
            'points': reward.total_points if reward else 0,
            'streak': reward.current_streak if reward else 0
        }
    })


@food_bp.route('/api/today-logs')
@login_required
def today_logs():
    """Get today's food logs"""
    user_id = session['user_id']
    today = date.today()
    
    logs = FoodLog.query.filter_by(
        user_id=user_id,
        log_date=today
    ).order_by(FoodLog.created_at.desc()).all()
    
    # Get health suggestion for targets
    health_suggestion = HealthSuggestion.query.filter_by(
        user_id=user_id,
        is_active=True
    ).order_by(HealthSuggestion.created_at.desc()).first()
    
    # Calculate totals
    totals = {
        'calories': sum(log.total_calories for log in logs),
        'protein': sum(log.total_protein for log in logs),
        'carbs': sum(log.total_carbs for log in logs),
        'fats': sum(log.total_fats for log in logs)
    }
    
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
            'time': log.created_at.strftime('%H:%M')
        } for log in logs],
        'totals': totals,
        'targets': {
            'calories': health_suggestion.calorie_target if health_suggestion else 0,
            'protein': health_suggestion.protein_target if health_suggestion else 0,
            'carbs': health_suggestion.carbs_target if health_suggestion else 0,
            'fats': health_suggestion.fats_target if health_suggestion else 0
        } if health_suggestion else None
    })


@food_bp.route('/api/delete-log/<int:log_id>', methods=['DELETE'])
@login_required
def delete_log(log_id):
    """Delete a food log"""
    user_id = session['user_id']
    
    food_log = FoodLog.query.filter_by(id=log_id, user_id=user_id).first()
    
    if not food_log:
        return jsonify({'success': False, 'message': 'Log not found'}), 404
    
    db.session.delete(food_log)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Log deleted successfully'
    })
