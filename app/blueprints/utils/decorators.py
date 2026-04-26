"""
Reusable route decorators.
"""

from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user


def admin_required(f):
    """Restrict route to users with role == 'admin'."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def user_required(f):
    """Restrict route to regular (non-admin) authenticated users."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in.', 'warning')
            return redirect(url_for('auth.login'))
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        return f(*args, **kwargs)
    return decorated
