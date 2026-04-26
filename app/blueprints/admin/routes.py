"""
Admin Blueprint — Admin Dashboard, User/Food/Reward management,
                  CSV Import & Export, Reward file uploads
"""

import csv
import io
import os
import uuid
from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, Response, stream_with_context,
                   current_app)
from flask_login import login_required
from app import db
from app.models.models import User, Food, FoodLog, Reward, UserStats, RewardRedemption
from app.blueprints.utils.decorators import admin_required
from sqlalchemy import func
from datetime import date, datetime

ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'txt'}

def _allowed_file(filename):
    return ('.' in filename and
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS)

def _save_reward_file(file_obj):
    """
    Validate, rename, and save an uploaded reward file.
    Returns (stored_filename, original_filename) on success, raises ValueError on failure.
    """
    original_name = file_obj.filename
    if not original_name:
        raise ValueError('No filename provided.')
    if not _allowed_file(original_name):
        raise ValueError(
            f'File type not allowed. Accepted: {", ".join(sorted(ALLOWED_EXTENSIONS)).upper()}.')
    ext = original_name.rsplit('.', 1)[1].lower()
    stored_name = f'{uuid.uuid4().hex}.{ext}'      # e.g. a3f8…b2.pdf
    dest = os.path.join(current_app.config['UPLOAD_FOLDER'], stored_name)
    file_obj.save(dest)
    return stored_name, original_name

def _delete_reward_file(stored_name):
    """Remove a reward file from disk; silently ignore if missing."""
    if not stored_name:
        return
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], stored_name)
    try:
        os.remove(path)
    except OSError:
        pass

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

        reward = Reward(name=name, points_required=pts, is_active=active)

        # Optional file upload
        file = request.files.get('reward_file')
        if file and file.filename:
            try:
                stored, original = _save_reward_file(file)
                reward.file_path = stored
                reward.file_name = original
            except ValueError as e:
                flash(str(e), 'danger')
                return render_template('admin/reward_form.html', reward=None)

        db.session.add(reward)
        db.session.commit()
        msg = f'Reward "{name}" added.'
        if reward.has_file:
            msg += f' File attached: {reward.file_name}'
        flash(msg, 'success')
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

        # Replace file if a new one is uploaded
        file = request.files.get('reward_file')
        if file and file.filename:
            try:
                stored, original = _save_reward_file(file)
                _delete_reward_file(reward.file_path)   # remove old file
                reward.file_path = stored
                reward.file_name = original
            except ValueError as e:
                flash(str(e), 'danger')
                return render_template('admin/reward_form.html', reward=reward)

        # Remove existing file if admin checked "remove file"
        if request.form.get('remove_file') and reward.has_file:
            _delete_reward_file(reward.file_path)
            reward.file_path = None
            reward.file_name = None

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
    _delete_reward_file(reward.file_path)   # clean up disk
    db.session.delete(reward)
    db.session.commit()
    flash('Reward deleted.', 'success')
    return redirect(url_for('admin.rewards'))


# ══════════════════════════════════════════════════════════════
#  CSV IMPORT
# ══════════════════════════════════════════════════════════════

@admin_bp.route('/import-foods', methods=['GET', 'POST'])
@login_required
@admin_required
def import_foods():
    """
    GET  → show upload form
    POST → process uploaded CSV file

    Expected CSV columns (header row required):
        name, calories_per_100g, protein_per_100g, carbs_per_100g, fats_per_100g
    """
    if request.method == 'POST':
        file = request.files.get('csv_file')

        # ── Basic validation ───────────────────────────────────
        if not file or file.filename == '':
            flash('No file selected. Please choose a CSV file.', 'danger')
            return redirect(url_for('admin.import_foods'))

        if not file.filename.lower().endswith('.csv'):
            flash('Only .csv files are accepted.', 'danger')
            return redirect(url_for('admin.import_foods'))

        # ── Parse CSV from memory (no disk write needed) ───────
        try:
            raw = file.read().decode('utf-8-sig')   # utf-8-sig strips BOM if present
        except UnicodeDecodeError:
            flash('File encoding error. Please save your CSV as UTF-8 and try again.', 'danger')
            return redirect(url_for('admin.import_foods'))

        reader    = csv.DictReader(io.StringIO(raw))
        required  = {'name', 'calories_per_100g', 'protein_per_100g',
                     'carbs_per_100g', 'fats_per_100g'}

        # ── Check header row ───────────────────────────────────
        if not reader.fieldnames:
            flash('CSV file is empty or has no header row.', 'danger')
            return redirect(url_for('admin.import_foods'))

        actual_cols = {c.strip().lower() for c in reader.fieldnames}
        if not required.issubset(actual_cols):
            missing = required - actual_cols
            flash(f'Missing columns: {", ".join(sorted(missing))}. '
                  f'Required: name, calories_per_100g, protein_per_100g, '
                  f'carbs_per_100g, fats_per_100g', 'danger')
            return redirect(url_for('admin.import_foods'))

        # ── Process rows ───────────────────────────────────────
        imported  = 0
        skipped   = 0
        errors    = []

        for line_num, row in enumerate(reader, start=2):   # start=2: row 1 is header
            try:
                name = row.get('name', '').strip()
                if not name:
                    errors.append(f'Row {line_num}: empty name — skipped.')
                    continue

                cal  = float(row.get('calories_per_100g', 0) or 0)
                prot = float(row.get('protein_per_100g',  0) or 0)
                carb = float(row.get('carbs_per_100g',    0) or 0)
                fat  = float(row.get('fats_per_100g',     0) or 0)

                # Skip duplicate names (case-insensitive)
                exists = Food.query.filter(
                    func.lower(Food.name) == name.lower()
                ).first()
                if exists:
                    skipped += 1
                    continue

                db.session.add(Food(
                    name=name,
                    calories_per_100g=cal,
                    protein_per_100g=prot,
                    carbs_per_100g=carb,
                    fats_per_100g=fat,
                ))
                imported += 1

            except (ValueError, TypeError) as e:
                errors.append(f'Row {line_num}: invalid number — {e}')

        db.session.commit()

        # ── Flash results ──────────────────────────────────────
        if imported:
            flash(f'{imported} food{"s" if imported != 1 else ""} imported successfully'
                  + (f' · {skipped} duplicate{"s" if skipped != 1 else ""} skipped.'
                     if skipped else '.'),
                  'success')
        elif skipped:
            flash(f'No new foods added — {skipped} duplicate{"s" if skipped != 1 else ""} skipped.', 'warning')
        else:
            flash('No foods were imported. Check the file and try again.', 'warning')

        if errors:
            for e in errors[:5]:        # show max 5 row errors
                flash(e, 'warning')
            if len(errors) > 5:
                flash(f'… and {len(errors) - 5} more row error(s).', 'warning')

        return redirect(url_for('admin.foods'))

    # GET — render upload form
    return render_template('admin/import_foods.html')


# ══════════════════════════════════════════════════════════════
#  CSV EXPORT
# ══════════════════════════════════════════════════════════════

def _csv_response(rows, headers, filename):
    """Build a streaming CSV download Response."""
    def generate():
        buf = io.StringIO()
        w   = csv.writer(buf)
        w.writerow(headers)
        yield buf.getvalue()
        for row in rows:
            buf = io.StringIO()
            w   = csv.writer(buf)
            w.writerow(row)
            yield buf.getvalue()

    ts = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    return Response(
        stream_with_context(generate()),
        mimetype='text/csv',
        headers={
            'Content-Disposition':
                f'attachment; filename="{filename}_{ts}.csv"'
        }
    )


@admin_bp.route('/export/foods')
@login_required
@admin_required
def export_foods():
    """Export all foods as CSV."""
    foods = Food.query.order_by(Food.name).all()
    headers = ['id', 'name', 'calories_per_100g',
               'protein_per_100g', 'carbs_per_100g', 'fats_per_100g']
    rows = [
        (f.id, f.name, f.calories_per_100g,
         f.protein_per_100g, f.carbs_per_100g, f.fats_per_100g)
        for f in foods
    ]
    return _csv_response(rows, headers, 'snts_foods')


@admin_bp.route('/export/food-logs')
@login_required
@admin_required
def export_food_logs():
    """Export all food logs (all users) as CSV."""
    logs = (FoodLog.query
            .join(User, FoodLog.user_id == User.id)
            .add_columns(User.username)
            .order_by(FoodLog.created_at.desc())
            .all())
    headers = ['log_id', 'username', 'food_name', 'quantity_g',
               'calories', 'protein_g', 'carbs_g', 'fats_g',
               'source', 'logged_at']
    rows = [
        (log.FoodLog.id, log.username, log.FoodLog.food_name,
         log.FoodLog.quantity, log.FoodLog.calories,
         log.FoodLog.protein, log.FoodLog.carbs, log.FoodLog.fats,
         'DB' if log.FoodLog.food_id else 'Manual',
         log.FoodLog.created_at.strftime('%Y-%m-%d %H:%M:%S'))
        for log in logs
    ]
    return _csv_response(rows, headers, 'snts_food_logs')


@admin_bp.route('/export/rewards')
@login_required
@admin_required
def export_rewards():
    """Export all rewards as CSV."""
    rewards = Reward.query.order_by(Reward.points_required).all()
    headers = ['id', 'name', 'points_required', 'is_active']
    rows = [
        (r.id, r.name, r.points_required, 'Yes' if r.is_active else 'No')
        for r in rewards
    ]
    return _csv_response(rows, headers, 'snts_rewards')


@admin_bp.route('/export/users')
@login_required
@admin_required
def export_users():
    """Export all non-admin users as CSV."""
    users = (User.query
             .filter(User.role != 'admin')
             .order_by(User.created_at.desc())
             .all())
    headers = ['id', 'username', 'email', 'height_cm', 'weight_kg',
               'age', 'gender', 'activity_level', 'bmi',
               'bmi_category', 'diet_type', 'joined']
    rows = [
        (u.id, u.username, u.email, u.height, u.weight,
         u.age, u.gender, u.activity_level, u.bmi,
         u.get_bmi_category(), u.diet_type,
         u.created_at.strftime('%Y-%m-%d %H:%M:%S'))
        for u in users
    ]
    return _csv_response(rows, headers, 'snts_users')


# ── Exports hub page ───────────────────────────────────────────
@admin_bp.route('/exports')
@login_required
@admin_required
def exports():
    total_foods   = Food.query.count()
    total_logs    = FoodLog.query.count()
    total_rewards = Reward.query.count()
    total_users   = User.query.filter(User.role != 'admin').count()
    return render_template('admin/exports.html',
        total_foods=total_foods,   total_logs=total_logs,
        total_rewards=total_rewards, total_users=total_users)


# ── Sample CSV download ────────────────────────────────────────
@admin_bp.route('/sample-csv')
@login_required
@admin_required
def download_sample_csv():
    """Serve a ready-to-use sample CSV for food import."""
    sample = (
        "name,calories_per_100g,protein_per_100g,carbs_per_100g,fats_per_100g\r\n"
        "Oats,389,16.9,66.3,6.9\r\n"
        "Greek Yogurt,59,10.0,3.6,0.4\r\n"
        "Almonds,579,21.2,21.6,49.9\r\n"
        "Banana,89,1.1,22.8,0.3\r\n"
        "Peanut Butter,588,25.1,20.1,50.4\r\n"
        "Sweet Potato,86,1.6,20.1,0.1\r\n"
        "Quinoa (cooked),120,4.4,21.3,1.9\r\n"
        "Cottage Cheese,98,11.1,3.4,4.3\r\n"
        "Broccoli,34,2.8,6.6,0.4\r\n"
        "Salmon,208,20.4,0.0,13.4\r\n"
    )
    return Response(
        sample,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename="snts_sample_foods.csv"'}
    )
