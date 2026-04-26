"""
Auth Blueprint — register, login, logout, forgot-password
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.models import User, UserStats
from datetime import datetime

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard') if current_user.role != 'admin'
                        else url_for('admin.dashboard'))
    if request.method == 'POST':
        username  = request.form.get('username', '').strip()
        password  = request.form.get('password', '')
        remember  = bool(request.form.get('remember'))
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            nxt = request.args.get('next')
            if user.role == 'admin':
                return redirect(nxt or url_for('admin.dashboard'))
            return redirect(nxt or url_for('user.dashboard'))
        flash('Invalid username or password.', 'danger')
    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))
    if request.method == 'POST':
        username  = request.form.get('username', '').strip()
        email     = request.form.get('email', '').strip().lower()
        password  = request.form.get('password', '')
        confirm   = request.form.get('confirm_password', '')
        height    = request.form.get('height',    type=float)
        weight    = request.form.get('weight',    type=float)
        age       = request.form.get('age',       type=int)
        gender    = request.form.get('gender',    '')
        activity  = request.form.get('activity_level', '')

        if not all([username, email, password, height, weight, age, gender, activity]):
            flash('All fields are required.', 'danger')
            return render_template('auth/register.html')
        if len(username) < 3:
            flash('Username must be at least 3 characters.', 'danger')
            return render_template('auth/register.html')
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('auth/register.html')
        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'danger')
            return render_template('auth/register.html')
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('auth/register.html')

        user = User(username=username, email=email,
                    height=height, weight=weight, age=age,
                    gender=gender, activity_level=activity)
        user.set_password(password)
        user.calculate_bmi()
        db.session.add(user)
        db.session.flush()
        db.session.add(UserStats(user_id=user.id, points=0, streak=0))
        db.session.commit()

        login_user(user)
        flash('Account created! Welcome to SNTS.', 'success')
        return redirect(url_for('user.dashboard'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username     = request.form.get('username', '').strip()
        new_password = request.form.get('new_password', '')
        confirm      = request.form.get('confirm_password', '')
        user = User.query.filter_by(username=username).first()
        if not user:
            flash('Username not found.', 'danger')
            return render_template('auth/forgot_password.html')
        if len(new_password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('auth/forgot_password.html')
        if new_password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/forgot_password.html')
        user.set_password(new_password)
        db.session.commit()
        flash('Password reset successfully. Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/forgot_password.html')
