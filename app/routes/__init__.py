"""
Routes Package Initializer
"""
from .auth import auth_bp
from .dashboard import dashboard_bp
from .food import food_bp
from .health import health_bp
from .history import history_bp
from .rewards import rewards_bp

__all__ = ['auth_bp', 'dashboard_bp', 'food_bp', 'health_bp', 'history_bp', 'rewards_bp']
