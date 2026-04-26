"""
Rewards & Gamification Routes
Points, streaks, badges, and rewards
"""
from flask import Blueprint, render_template, jsonify, session
from app.models import Reward
from app.routes.auth import login_required
from app.utils import get_reward_options

rewards_bp = Blueprint('rewards', __name__)


@rewards_bp.route('/rewards')
@login_required
def rewards():
    """Rewards page"""
    return render_template('rewards.html')


@rewards_bp.route('/api/reward-data')
@login_required
def reward_data():
    """Get reward and gamification data"""
    user_id = session['user_id']
    
    reward = Reward.query.filter_by(user_id=user_id).first()
    
    if not reward:
        return jsonify({
            'success': True,
            'points': 0,
            'current_streak': 0,
            'longest_streak': 0,
            'badges': [],
            'available_rewards': []
        })
    
    badges_list = [b.strip() for b in reward.badges.split(',') if b.strip()]
    available_rewards = get_reward_options(reward.total_points)
    
    return jsonify({
        'success': True,
        'points': reward.total_points,
        'current_streak': reward.current_streak,
        'longest_streak': reward.longest_streak,
        'last_log_date': reward.last_log_date.strftime('%Y-%m-%d') if reward.last_log_date else None,
        'badges': badges_list,
        'available_rewards': available_rewards
    })
