"""
Admin Blueprint — Admin Dashboard, User/Food/Reward management
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models.models import User, Food, FoodLog, Reward, UserStats
from app.blueprints.utils.decorators import admin_required
from sqlalchemy import func
from datetime import date

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_users   = User.query.filter(User.role != 'admin').count()
    total_logs    = FoodLog.query.count()
    today_logs    = FoodLog.query.filter(func.date(FoodLog.created_at) == date.today()).count()
    total_foods   = Food.query.count()
    total_rewards = Reward.query.filter_by(is_active=True).count()
    recent_users  = User.query.filter(User.role != 'admin')\
        .order_by(User.created_at.desc()).limit(10).all()

    return render_template('admin/dashboard.html',
        total_users=total_users,   total_logs=total_logs,
        today_logs=today_logs,     total_foods=total_foods,
        total_rewards=total_rewards, recent_users=recent_users)


# ── Users ─────────────────────────────────────────────────────
@admin_bp.route('/users')
@login_required
@admin_required
def users():
    all_users = User.query.filter(User.role != 'admin')\
        .order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users)


@admin_bp.route('/delete-user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        flash('Cannot delete admin account.', 'danger')
        return redirect(url_for('admin.users'))
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.username} deleted.', 'success')
    return redirect(url_for('admin.users'))


# ── Foods ─────────────────────────────────────────────────────
@admin_bp.route('/foods')
@login_required
@admin_required
def foods():
    search = request.args.get('search', '').strip()
    query = Food.query
    if search:
        query = query.filter(Food.name.ilike(f'%{search}%'))
    all_foods = query.order_by(Food.name).all()
    return render_template('admin/foods.html', foods=all_foods, search=search)


@admin_bp.route('/add-food', methods=['GET', 'POST'])
@login_required
@admin_required
def add_food():
    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        calories = request.form.get('calories', type=float)
        protein  = request.form.get('protein',  type=float)
        carbs    = request.form.get('carbs',    type=float)
        fats     = request.form.get('fats',     type=float)
        if not name or calories is None:
            flash('Name and calories are required.', 'danger')
            return render_template('admin/food_form.html', food=None)
        if Food.query.filter_by(name=name).first():
            flash('A food with that name already exists.', 'danger')
            return render_template('admin/food_form.html', food=None)
        db.session.add(Food(name=name, calories_per_100g=calories,
                            protein_per_100g=protein or 0,
                            carbs_per_100g=carbs or 0,
                            fats_per_100g=fats or 0))
        db.session.commit()
        flash(f'{name} added to database.', 'success')
        return redirect(url_for('admin.foods'))
    return render_template('admin/food_form.html', food=None)


@admin_bp.route('/edit-food/<int:food_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_food(food_id):
    food = Food.query.get_or_404(food_id)
    if request.method == 'POST':
        food.name              = request.form.get('name', food.name).strip()
        food.calories_per_100g = request.form.get('calories', type=float) or food.calories_per_100g
        food.protein_per_100g  = request.form.get('protein',  type=float) or 0
        food.carbs_per_100g    = request.form.get('carbs',    type=float) or 0
        food.fats_per_100g     = request.form.get('fats',     type=float) or 0
        db.session.commit()
        flash(f'{food.name} updated.', 'success')
        return redirect(url_for('admin.foods'))
    return render_template('admin/food_form.html', food=food)


@admin_bp.route('/delete-food/<int:food_id>', methods=['POST'])
@login_required
@admin_required
def delete_food(food_id):
    food = Food.query.get_or_404(food_id)
    db.session.delete(food)
    db.session.commit()
    flash(f'{food.name} deleted.', 'success')
    return redirect(url_for('admin.foods'))


# ── Rewards ───────────────────────────────────────────────────
@admin_bp.route('/rewards')
@login_required
@admin_required
def rewards():
    all_rewards = Reward.query.order_by(Reward.points_required).all()
    return render_template('admin/rewards.html', rewards=all_rewards)


@admin_bp.route('/add-reward', methods=['GET', 'POST'])
@login_required
@admin_required
def add_reward():
    if request.method == 'POST':
        name   = request.form.get('name', '').strip()
        pts    = request.form.get('points_required', type=int)
        active = bool(request.form.get('is_active'))
        if not name or not pts:
            flash('Name and points are required.', 'danger')
            return render_template('admin/reward_form.html', reward=None)
        db.session.add(Reward(name=name, points_required=pts, is_active=active))
        db.session.commit()
        flash(f'Reward "{name}" added.', 'success')
        return redirect(url_for('admin.rewards'))
    return render_template('admin/reward_form.html', reward=None)


@admin_bp.route('/edit-reward/<int:reward_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_reward(reward_id):
    reward = Reward.query.get_or_404(reward_id)
    if request.method == 'POST':
        reward.name            = request.form.get('name', reward.name).strip()
        reward.points_required = request.form.get('points_required', type=int) or reward.points_required
        reward.is_active       = bool(request.form.get('is_active'))
        db.session.commit()
        flash(f'Reward "{reward.name}" updated.', 'success')
        return redirect(url_for('admin.rewards'))
    return render_template('admin/reward_form.html', reward=reward)


@admin_bp.route('/toggle-reward/<int:reward_id>', methods=['POST'])
@login_required
@admin_required
def toggle_reward(reward_id):
    reward = Reward.query.get_or_404(reward_id)
    reward.is_active = not reward.is_active
    db.session.commit()
    state = 'enabled' if reward.is_active else 'disabled'
    flash(f'Reward "{reward.name}" {state}.', 'success')
    return redirect(url_for('admin.rewards'))


@admin_bp.route('/delete-reward/<int:reward_id>', methods=['POST'])
@login_required
@admin_required
def delete_reward(reward_id):
    reward = Reward.query.get_or_404(reward_id)
    db.session.delete(reward)
    db.session.commit()
    flash(f'Reward deleted.', 'success')
    return redirect(url_for('admin.rewards'))
