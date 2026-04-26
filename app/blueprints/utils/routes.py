"""
Utils Blueprint — JSON APIs for food search and chart data
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.models import Food, FoodLog
from sqlalchemy import func
from datetime import date, timedelta

utils_bp = Blueprint('utils', __name__)


@utils_bp.route('/search-foods')
@login_required
def search_foods():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])
    foods = Food.query.filter(Food.name.ilike(f'%{q}%'))\
        .order_by(Food.name).limit(10).all()
    return jsonify([{
        'id':       f.id,
        'name':     f.name,
        'calories': f.calories_per_100g,
        'protein':  f.protein_per_100g,
        'carbs':    f.carbs_per_100g,
        'fats':     f.fats_per_100g,
    } for f in foods])


@utils_bp.route('/chart-data')
@login_required
def chart_data():
    period = request.args.get('period', 'daily')
    today  = date.today()

    # ── Bar chart: daily calories for last 7 days ──────────
    bar_labels, bar_data = [], []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        total = db.session.query(
            func.coalesce(func.sum(FoodLog.calories), 0)
        ).filter(
            FoodLog.user_id == current_user.id,
            func.date(FoodLog.created_at) == day
        ).scalar()
        bar_labels.append(day.strftime('%a'))
        bar_data.append(round(total, 1))

    # ── Pie chart: macro split ─────────────────────────────
    if period == 'daily':
        start = today
    elif period == 'weekly':
        start = today - timedelta(days=6)
    else:  # monthly
        start = today - timedelta(days=29)

    macros = db.session.query(
        func.coalesce(func.sum(FoodLog.protein), 0).label('protein'),
        func.coalesce(func.sum(FoodLog.carbs),   0).label('carbs'),
        func.coalesce(func.sum(FoodLog.fats),    0).label('fats'),
    ).filter(
        FoodLog.user_id == current_user.id,
        func.date(FoodLog.created_at) >= start
    ).first()

    return jsonify({
        'bar': {'labels': bar_labels, 'data': bar_data},
        'pie': {
            'protein': round(macros.protein, 1),
            'carbs':   round(macros.carbs,   1),
            'fats':    round(macros.fats,     1),
        }
    })
