"""
Health & Hydration Routes
BMI updates, diet preferences, and water tracking
"""
from flask import Blueprint, render_template, request, jsonify, session
from app.models import db, User, HealthSuggestion, HydrationLog, Reward
from app.routes.auth import login_required
from app.utils import (calculate_bmi, get_bmi_category, suggest_diet_type, 
                       calculate_diet_targets, calculate_water_intake)
from datetime import date

health_bp = Blueprint('health', __name__)


@health_bp.route('/health-profile')
@login_required
def health_profile():
    """Health profile page"""
    return render_template('health_profile.html')


@health_bp.route('/api/health-data')
@login_required
def get_health_data():
    """Get current health data"""
    user_id = session['user_id']
    
    user = User.query.get(user_id)
    health_suggestion = HealthSuggestion.query.filter_by(
        user_id=user_id,
        is_active=True
    ).order_by(HealthSuggestion.created_at.desc()).first()
    
    return jsonify({
        'success': True,
        'user': {
            'height': user.height,
            'weight': user.weight,
            'age': user.age,
            'gender': user.gender
        },
        'health_suggestion': {
            'bmi': health_suggestion.bmi,
            'bmi_category': health_suggestion.bmi_category,
            'suggested_diet': health_suggestion.suggested_diet,
            'chosen_diet': health_suggestion.chosen_diet,
            'targets': {
                'calories': health_suggestion.calorie_target,
                'protein': health_suggestion.protein_target,
                'carbs': health_suggestion.carbs_target,
                'fats': health_suggestion.fats_target
            }
        } if health_suggestion else None
    })


@health_bp.route('/api/update-diet', methods=['POST'])
@login_required
def update_diet():
    """Update diet preference"""
    user_id = session['user_id']
    data = request.get_json()
    
    diet_type = data.get('diet_type')
    
    if diet_type not in ['Bulking', 'Cutting', 'Maintenance']:
        return jsonify({'success': False, 'message': 'Invalid diet type'}), 400
    
    user = User.query.get(user_id)
    
    # Deactivate old suggestions
    HealthSuggestion.query.filter_by(user_id=user_id).update({'is_active': False})
    
    # Calculate new targets
    bmi = calculate_bmi(user.weight, user.height)
    bmi_category = get_bmi_category(bmi)
    suggested_diet = suggest_diet_type(bmi, bmi_category)
    
    targets = calculate_diet_targets(
        user.weight, user.height, user.age, user.gender, diet_type
    )
    
    # Create new health suggestion
    new_suggestion = HealthSuggestion(
        user_id=user_id,
        bmi=bmi,
        bmi_category=bmi_category,
        suggested_diet=suggested_diet,
        chosen_diet=diet_type,
        calorie_target=targets['calorie_target'],
        protein_target=targets['protein_target'],
        carbs_target=targets['carbs_target'],
        fats_target=targets['fats_target']
    )
    
    db.session.add(new_suggestion)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Diet updated successfully',
        'targets': targets
    })


@health_bp.route('/api/update-weight', methods=['POST'])
@login_required
def update_weight():
    """Update user weight and recalculate metrics"""
    user_id = session['user_id']
    data = request.get_json()
    
    new_weight = data.get('weight')
    
    try:
        new_weight = float(new_weight)
        if new_weight <= 0 or new_weight > 300:
            return jsonify({'success': False, 'message': 'Invalid weight'}), 400
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Invalid weight'}), 400
    
    user = User.query.get(user_id)
    user.weight = new_weight
    
    # Recalculate health metrics
    bmi = calculate_bmi(user.weight, user.height)
    bmi_category = get_bmi_category(bmi)
    suggested_diet = suggest_diet_type(bmi, bmi_category)
    
    # Get current diet preference
    current_suggestion = HealthSuggestion.query.filter_by(
        user_id=user_id,
        is_active=True
    ).order_by(HealthSuggestion.created_at.desc()).first()
    
    chosen_diet = current_suggestion.chosen_diet if current_suggestion else suggested_diet
    
    # Deactivate old suggestions
    HealthSuggestion.query.filter_by(user_id=user_id).update({'is_active': False})
    
    # Calculate new targets
    targets = calculate_diet_targets(
        user.weight, user.height, user.age, user.gender, chosen_diet
    )
    
    # Create new suggestion
    new_suggestion = HealthSuggestion(
        user_id=user_id,
        bmi=bmi,
        bmi_category=bmi_category,
        suggested_diet=suggested_diet,
        chosen_diet=chosen_diet,
        calorie_target=targets['calorie_target'],
        protein_target=targets['protein_target'],
        carbs_target=targets['carbs_target'],
        fats_target=targets['fats_target']
    )
    
    db.session.add(new_suggestion)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Weight updated successfully',
        'new_bmi': bmi,
        'bmi_category': bmi_category,
        'suggested_diet': suggested_diet,
        'targets': targets
    })


@health_bp.route('/api/log-hydration', methods=['POST'])
@login_required
def log_hydration():
    """Log water intake"""
    user_id = session['user_id']
    data = request.get_json()
    
    amount = data.get('amount')
    
    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({'success': False, 'message': 'Invalid amount'}), 400
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Invalid amount'}), 400
    
    user = User.query.get(user_id)
    target = calculate_water_intake(user.weight)
    
    today = date.today()
    
    # Check if hydration log exists for today
    hydration_log = HydrationLog.query.filter_by(
        user_id=user_id,
        log_date=today
    ).first()
    
    if hydration_log:
        hydration_log.water_intake += amount
    else:
        hydration_log = HydrationLog(
            user_id=user_id,
            water_intake=amount,
            target_intake=target,
            log_date=today
        )
        db.session.add(hydration_log)
    
    # Check if target achieved and update rewards
    if hydration_log.water_intake >= hydration_log.target_intake:
        reward = Reward.query.filter_by(user_id=user_id).first()
        if reward:
            # Check if bonus already awarded today
            if reward.last_log_date != today or reward.total_points % 50 != 0:
                reward.total_points += 50  # Bonus for hydration goal
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Hydration logged successfully',
        'current': hydration_log.water_intake,
        'target': hydration_log.target_intake,
        'percentage': round((hydration_log.water_intake / hydration_log.target_intake) * 100, 1)
    })


@health_bp.route('/api/hydration-status')
@login_required
def hydration_status():
    """Get today's hydration status"""
    user_id = session['user_id']
    today = date.today()
    
    user = User.query.get(user_id)
    target = calculate_water_intake(user.weight)
    
    hydration_log = HydrationLog.query.filter_by(
        user_id=user_id,
        log_date=today
    ).first()
    
    current = hydration_log.water_intake if hydration_log else 0
    
    return jsonify({
        'success': True,
        'current': current,
        'target': target,
        'percentage': round((current / target) * 100, 1) if target > 0 else 0
    })
