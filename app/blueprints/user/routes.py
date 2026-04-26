"""
User Blueprint — Dashboard, Food Logging, Rewards, Profile,
                 History, Water, Data Portability (Export / Import)
"""

import json
from datetime import date, timedelta, datetime
from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, jsonify, session, Response)
from flask_login import login_required, current_user
from app import db
from app.models.models import User, Food, FoodLog, Reward, UserStats
from sqlalchemy import func

user_bp = Blueprint('user', __name__)


# ── Dashboard ─────────────────────────────────────────────────
@user_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))

    today = date.today()

    # Today's totals
    totals = db.session.query(
        func.coalesce(func.sum(FoodLog.calories), 0).label('calories'),
        func.coalesce(func.sum(FoodLog.protein),  0).label('protein'),
        func.coalesce(func.sum(FoodLog.carbs),    0).label('carbs'),
        func.coalesce(func.sum(FoodLog.fats),     0).label('fats'),
    ).filter(
        FoodLog.user_id == current_user.id,
        func.date(FoodLog.created_at) == today
    ).first()

    calories_today = round(totals.calories, 1)
    protein_today  = round(totals.protein,  1)
    carbs_today    = round(totals.carbs,    1)
    fats_today     = round(totals.fats,     1)

    # Ensure stats exist
    stats = UserStats.query.filter_by(user_id=current_user.id).first()
    if not stats:
        stats = UserStats(user_id=current_user.id, points=0, streak=0)
        db.session.add(stats); db.session.commit()

    calorie_target = current_user.get_calorie_target()
    protein_target = round(current_user.weight * 1.6)
    carbs_target   = round((calorie_target * 0.45) / 4)
    fats_target    = round((calorie_target * 0.25) / 9)

    def pct(val, target):
        return min(100, round((val / target * 100) if target > 0 else 0))

    cal_percent  = pct(calories_today, calorie_target)
    protein_pct  = pct(protein_today,  protein_target)
    carbs_pct    = pct(carbs_today,    carbs_target)
    fats_pct     = pct(fats_today,     fats_target)

    # Today's log
    today_logs = FoodLog.query.filter(
        FoodLog.user_id == current_user.id,
        func.date(FoodLog.created_at) == today
    ).order_by(FoodLog.created_at.desc()).all()

    # Weekly summary (last 7 days)
    week_start = today - timedelta(days=6)
    week = db.session.query(
        func.coalesce(func.sum(FoodLog.calories), 0).label('calories'),
        func.coalesce(func.sum(FoodLog.protein),  0).label('protein'),
        func.count(FoodLog.id).label('log_count'),
    ).filter(
        FoodLog.user_id == current_user.id,
        func.date(FoodLog.created_at) >= week_start
    ).first()

    # Suggestions
    remaining = calorie_target - calories_today
    suggestions = []
    if remaining > 50:
        suggestions = Food.query.filter(
            Food.calories_per_100g <= remaining
        ).order_by(Food.protein_per_100g.desc()).limit(3).all()

    water_glasses = session.get('water_glasses', 0)

    return render_template('user/dashboard.html',
        calories_today=calories_today, protein_today=protein_today,
        carbs_today=carbs_today,       fats_today=fats_today,
        calorie_target=calorie_target, protein_target=protein_target,
        carbs_target=carbs_target,     fats_target=fats_target,
        cal_percent=cal_percent,       protein_pct=protein_pct,
        carbs_pct=carbs_pct,           fats_pct=fats_pct,
        stats=stats,                   suggestions=suggestions,
        today_logs=today_logs,         bmi_category=current_user.get_bmi_category(),
        week_calories=round(week.calories, 0),
        week_protein=round(week.protein, 1),
        week_log_count=week.log_count,
        water_glasses=water_glasses,
    )


# ── Food Log ──────────────────────────────────────────────────
@user_bp.route('/food-log', methods=['GET', 'POST'])
@login_required
def food_log():
    if current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        entry_type = request.form.get('entry_type', 'search')

        if entry_type == 'search':
            food_id  = request.form.get('food_id', type=int)
            quantity = request.form.get('quantity', type=float)
            if not food_id or not quantity or quantity <= 0:
                flash('Please select a food and enter a valid quantity.', 'danger')
                return redirect(url_for('user.food_log'))
            food = Food.query.get(food_id)
            if not food:
                flash('Food not found.', 'danger')
                return redirect(url_for('user.food_log'))
            nutrients = food.get_nutrients_for_quantity(quantity)
            log = FoodLog(user_id=current_user.id, food_id=food.id,
                          food_name=food.name, quantity=quantity,
                          **nutrients)

        elif entry_type == 'manual':
            food_name = request.form.get('food_name', '').strip()
            quantity  = request.form.get('quantity',  type=float)
            calories  = request.form.get('calories',  type=float)
            protein   = request.form.get('protein',   type=float) or 0.0
            carbs     = request.form.get('carbs',     type=float) or 0.0
            fats      = request.form.get('fats',      type=float) or 0.0
            if not food_name or not quantity or calories is None:
                flash('Please fill in all required fields.', 'danger')
                return redirect(url_for('user.food_log'))
            log = FoodLog(user_id=current_user.id, food_id=None,
                          food_name=food_name, quantity=quantity,
                          calories=calories, protein=protein,
                          carbs=carbs, fats=fats)
        else:
            flash('Invalid entry type.', 'danger')
            return redirect(url_for('user.food_log'))

        db.session.add(log)

        stats = UserStats.query.filter_by(user_id=current_user.id).first()
        if not stats:
            stats = UserStats(user_id=current_user.id, points=0, streak=0)
            db.session.add(stats)
        stats.update_streak_and_points(10)
        db.session.commit()

        flash(f'{log.food_name} logged successfully! +10 points earned.', 'success')
        return redirect(url_for('user.dashboard'))

    today = date.today()
    today_logs = FoodLog.query.filter(
        FoodLog.user_id == current_user.id,
        func.date(FoodLog.created_at) == today
    ).order_by(FoodLog.created_at.desc()).all()

    # Recent foods: last 5 unique food_names
    recent_subq = db.session.query(
        FoodLog.food_name,
        func.max(FoodLog.id).label('max_id')
    ).filter(
        FoodLog.user_id == current_user.id
    ).group_by(FoodLog.food_name).order_by(
        func.max(FoodLog.created_at).desc()
    ).limit(5).subquery()

    recent_foods = db.session.query(FoodLog).join(
        recent_subq, FoodLog.id == recent_subq.c.max_id
    ).order_by(FoodLog.created_at.desc()).all()

    all_foods = Food.query.order_by(Food.name).all()
    return render_template('user/food_log.html',
        today_logs=today_logs, all_foods=all_foods, recent_foods=recent_foods)


# ── Delete Log ────────────────────────────────────────────────
@user_bp.route('/delete-log/<int:log_id>', methods=['POST'])
@login_required
def delete_log(log_id):
    log = FoodLog.query.filter_by(id=log_id, user_id=current_user.id).first()
    if not log:
        flash('Entry not found.', 'danger')
        return redirect(url_for('user.food_log'))
    db.session.delete(log)
    db.session.commit()
    flash('Entry deleted.', 'info')
    return redirect(url_for('user.food_log'))


# ── Rewards ───────────────────────────────────────────────────
@user_bp.route('/rewards')
@login_required
def rewards():
    stats = UserStats.query.filter_by(user_id=current_user.id).first()
    if not stats:
        stats = UserStats(user_id=current_user.id, points=0, streak=0)
        db.session.add(stats); db.session.commit()
    active_rewards = Reward.query.filter_by(is_active=True).order_by(Reward.points_required).all()
    return render_template('user/rewards.html', rewards=active_rewards, stats=stats)


@user_bp.route('/redeem-reward/<int:reward_id>', methods=['POST'])
@login_required
def redeem_reward(reward_id):
    reward = Reward.query.get(reward_id)
    if not reward or not reward.is_active:
        flash('Reward not found or inactive.', 'danger')
        return redirect(url_for('user.rewards'))
    stats = UserStats.query.filter_by(user_id=current_user.id).first()
    if not stats or stats.points < reward.points_required:
        flash(f'Not enough points. You need {reward.points_required} points.', 'warning')
        return redirect(url_for('user.rewards'))
    stats.points -= reward.points_required
    db.session.commit()
    flash(f'Reward redeemed: {reward.name}. Congratulations!', 'success')
    return redirect(url_for('user.rewards'))


# ── Profile ───────────────────────────────────────────────────
@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        height       = request.form.get('height',         type=float)
        weight       = request.form.get('weight',         type=float)
        age          = request.form.get('age',            type=int)
        activity     = request.form.get('activity_level', '')
        diet_type    = request.form.get('diet_type',      '')
        if height and weight and age:
            current_user.height         = height
            current_user.weight         = weight
            current_user.age            = age
            current_user.activity_level = activity or current_user.activity_level
            # Only update diet_type if explicitly chosen
            if diet_type:
                current_user.diet_type = diet_type
            current_user.calculate_bmi()
            # If user explicitly selected diet_type, override the BMI suggestion
            if diet_type:
                current_user.diet_type = diet_type
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        else:
            flash('Please fill in all required fields.', 'danger')
        return redirect(url_for('user.profile'))

    stats = UserStats.query.filter_by(user_id=current_user.id).first()
    return render_template('user/profile.html', stats=stats)


# ── History ───────────────────────────────────────────────────
@user_bp.route('/history')
@login_required
def history():
    page = request.args.get('page', 1, type=int)
    logs = FoodLog.query.filter_by(user_id=current_user.id)\
        .order_by(FoodLog.created_at.desc())\
        .paginate(page=page, per_page=20, error_out=False)
    return render_template('user/history.html', logs=logs)


# ── Water tracker ─────────────────────────────────────────────
@user_bp.route('/water', methods=['POST'])
@login_required
def update_water():
    glasses = request.form.get('glasses', type=int, default=0)
    if 0 <= glasses <= 20:
        session['water_glasses'] = glasses
        session.modified = True
    return redirect(url_for('user.dashboard'))


# ══════════════════════════════════════════════════════════════
#  DATA PORTABILITY — EXPORT
# ══════════════════════════════════════════════════════════════

@user_bp.route('/export-data')
@login_required
def export_data():
    """
    Build a JSON snapshot of the current user's data and return it
    as a downloadable file.  Only touches the logged-in user's rows.
    """
    u = current_user
    stats = UserStats.query.filter_by(user_id=u.id).first()

    # ── Profile section ────────────────────────────────────────
    profile = {
        'username':       u.username,
        'email':          u.email,
        'height_cm':      u.height,
        'weight_kg':      u.weight,
        'age':            u.age,
        'gender':         u.gender,
        'activity_level': u.activity_level,
        'diet_type':      u.diet_type,
        'bmi':            u.bmi,
        'bmi_category':   u.get_bmi_category(),
        'calorie_target': u.get_calorie_target(),
        'joined':         u.created_at.strftime('%Y-%m-%d %H:%M:%S'),
    }

    # ── Stats section ──────────────────────────────────────────
    user_stats = {
        'points':        stats.points        if stats else 0,
        'streak_days':   stats.streak        if stats else 0,
        'last_log_date': str(stats.last_log_date) if (stats and stats.last_log_date) else None,
    }

    # ── Food logs section ──────────────────────────────────────
    logs = (FoodLog.query
            .filter_by(user_id=u.id)
            .order_by(FoodLog.created_at.desc())
            .all())

    food_logs = [
        {
            'food_name':  log.food_name,
            'quantity_g': log.quantity,
            'calories':   log.calories,
            'protein_g':  log.protein,
            'carbs_g':    log.carbs,
            'fats_g':     log.fats,
            'source':     'database' if log.food_id else 'manual',
            'logged_at':  log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
        for log in logs
    ]

    # ── Assemble payload ───────────────────────────────────────
    payload = {
        '_snts_version': '1.0',
        '_exported_at':  datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        'profile':       profile,
        'stats':         user_stats,
        'food_logs':     food_logs,
    }

    ts       = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    filename = f'snts_{u.username}_{ts}.json'

    return Response(
        json.dumps(payload, indent=2),
        mimetype='application/json',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )


# ══════════════════════════════════════════════════════════════
#  DATA PORTABILITY — IMPORT
# ══════════════════════════════════════════════════════════════

@user_bp.route('/import-data', methods=['GET', 'POST'])
@login_required
def import_data():
    """
    GET  → show import form (rendered inside profile page via redirect,
           but also has a standalone minimal page as fallback).
    POST → validate JSON, update profile + stats + re-insert food logs.

    Rules
    -----
    * Only affects current_user — never touches another user's rows.
    * Food logs are APPENDED (not replaced) so existing logs are kept.
    * Profile fields are UPDATED only when the JSON value is valid.
    * Stats (points, streak) are REPLACED with imported values.
    """
    if request.method == 'GET':
        # Redirect back to profile — the import form lives there
        return redirect(url_for('user.profile') + '#import-section')

    # ── Read & decode uploaded file ────────────────────────────
    file = request.files.get('json_file')
    if not file or file.filename == '':
        flash('No file selected. Please choose a .json file.', 'danger')
        return redirect(url_for('user.profile'))

    if not file.filename.lower().endswith('.json'):
        flash('Only .json files are accepted.', 'danger')
        return redirect(url_for('user.profile'))

    try:
        raw  = file.read().decode('utf-8')
        data = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        flash(f'Could not read file: {e}', 'danger')
        return redirect(url_for('user.profile'))

    # ── Top-level structure check ──────────────────────────────
    if not isinstance(data, dict):
        flash('Invalid file format: expected a JSON object at the top level.', 'danger')
        return redirect(url_for('user.profile'))

    if '_snts_version' not in data:
        flash('This file was not exported from SNTS. '
              'Please use a file downloaded via "Export My Data".', 'warning')
        return redirect(url_for('user.profile'))

    imported_logs   = 0
    skipped_logs    = 0
    profile_updated = False
    stats_updated   = False

    # ── 1. Update profile ──────────────────────────────────────
    prof = data.get('profile', {})
    if isinstance(prof, dict):
        try:
            h = float(prof.get('height_cm') or 0)
            w = float(prof.get('weight_kg') or 0)
            a = int(prof.get('age')         or 0)
            if 50 <= h <= 300:
                current_user.height = h
            if 10 <= w <= 500:
                current_user.weight = w
            if 5  <= a <= 120:
                current_user.age = a

            act = prof.get('activity_level', '')
            if act in ('sedentary', 'moderate', 'active'):
                current_user.activity_level = act

            dt = prof.get('diet_type', '')
            if dt in ('bulking', 'maintenance', 'cutting'):
                current_user.diet_type = dt

            current_user.calculate_bmi()
            # Honour explicit diet_type over BMI auto-suggestion
            if dt in ('bulking', 'maintenance', 'cutting'):
                current_user.diet_type = dt

            profile_updated = True
        except (TypeError, ValueError):
            flash('Some profile fields were invalid and skipped.', 'warning')

    # ── 2. Update stats ────────────────────────────────────────
    st = data.get('stats', {})
    if isinstance(st, dict):
        try:
            pts    = int(st.get('points', 0)      or 0)
            streak = int(st.get('streak_days', 0) or 0)
            lld    = st.get('last_log_date')

            stats = UserStats.query.filter_by(user_id=current_user.id).first()
            if not stats:
                stats = UserStats(user_id=current_user.id)
                db.session.add(stats)

            stats.points = max(0, pts)
            stats.streak = max(0, streak)
            if lld:
                try:
                    stats.last_log_date = date.fromisoformat(str(lld))
                except ValueError:
                    pass   # ignore bad date string

            stats_updated = True
        except (TypeError, ValueError):
            flash('Stats section was invalid and skipped.', 'warning')

    # ── 3. Import food logs ────────────────────────────────────
    logs_raw = data.get('food_logs', [])
    if isinstance(logs_raw, list):
        for entry in logs_raw:
            if not isinstance(entry, dict):
                skipped_logs += 1
                continue

            food_name = str(entry.get('food_name', '')).strip()
            if not food_name:
                skipped_logs += 1
                continue

            try:
                quantity = float(entry.get('quantity_g') or 100)
                calories = float(entry.get('calories')   or 0)
                protein  = float(entry.get('protein_g')  or 0)
                carbs    = float(entry.get('carbs_g')    or 0)
                fats     = float(entry.get('fats_g')     or 0)
            except (TypeError, ValueError):
                skipped_logs += 1
                continue

            # Parse logged_at — fall back to now if missing / bad
            logged_at_str = entry.get('logged_at', '')
            try:
                logged_at = datetime.strptime(logged_at_str, '%Y-%m-%d %H:%M:%S')
            except (ValueError, TypeError):
                logged_at = datetime.utcnow()

            db.session.add(FoodLog(
                user_id   = current_user.id,
                food_id   = None,           # imported logs have no DB food reference
                food_name = food_name,
                quantity  = quantity,
                calories  = calories,
                protein   = protein,
                carbs     = carbs,
                fats      = fats,
                created_at= logged_at,
            ))
            imported_logs += 1

    db.session.commit()

    # ── Flash summary ──────────────────────────────────────────
    parts = []
    if profile_updated:
        parts.append('profile updated')
    if stats_updated:
        parts.append('points & streak restored')
    if imported_logs:
        parts.append(f'{imported_logs} food log{"s" if imported_logs != 1 else ""} imported')
    if skipped_logs:
        parts.append(f'{skipped_logs} log row{"s" if skipped_logs != 1 else ""} skipped')

    if parts:
        flash('Import successful — ' + ', '.join(parts) + '.', 'success')
    else:
        flash('Nothing was imported. The file may be empty or already applied.', 'warning')

    return redirect(url_for('user.profile'))
