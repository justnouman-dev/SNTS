"""
SNTS — ORM Models
Tables: users, foods, food_logs, rewards, user_stats
"""

from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ── User ─────────────────────────────────────────────────────
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id             = db.Column(db.Integer, primary_key=True)
    username       = db.Column(db.String(80), unique=True, nullable=False)
    email          = db.Column(db.String(120), unique=True, nullable=False)
    password_hash  = db.Column(db.String(256), nullable=False)
    height         = db.Column(db.Float, default=170.0)
    weight         = db.Column(db.Float, default=70.0)
    age            = db.Column(db.Integer, default=25)
    gender         = db.Column(db.String(10), default='male')
    activity_level = db.Column(db.String(20), default='moderate')
    role           = db.Column(db.String(20), default='user')
    bmi            = db.Column(db.Float, default=0.0)
    diet_type      = db.Column(db.String(20), default='maintenance')
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    food_logs = db.relationship('FoodLog', backref='user', lazy=True,
                                cascade='all, delete-orphan')
    stats     = db.relationship('UserStats', backref='user', uselist=False,
                                cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def calculate_bmi(self):
        if self.height and self.weight and self.height > 0:
            h_m = self.height / 100
            self.bmi = round(self.weight / (h_m ** 2), 1)
            # Auto diet suggestion
            if self.bmi < 18.5:
                self.diet_type = 'bulking'
            elif self.bmi <= 24.9:
                self.diet_type = 'maintenance'
            else:
                self.diet_type = 'cutting'
        return self.bmi

    def get_bmi_category(self):
        bmi = self.bmi or 0
        if   bmi < 18.5: return 'Underweight'
        elif bmi < 25:   return 'Normal'
        elif bmi < 30:   return 'Overweight'
        else:            return 'Obese'

    def get_calorie_target(self):
        """Harris-Benedict TDEE."""
        activity_mult = {'sedentary': 1.2, 'moderate': 1.55, 'active': 1.725}
        mult = activity_mult.get(self.activity_level, 1.55)
        if self.gender == 'female':
            bmr = 655 + (9.6 * self.weight) + (1.8 * self.height) - (4.7 * self.age)
        else:
            bmr = 66 + (13.7 * self.weight) + (5 * self.height) - (6.8 * self.age)
        tdee = bmr * mult
        adjust = {'bulking': 300, 'cutting': -300, 'maintenance': 0}
        return round(tdee + adjust.get(self.diet_type, 0))


# ── Food ─────────────────────────────────────────────────────
class Food(db.Model):
    __tablename__ = 'foods'

    id               = db.Column(db.Integer, primary_key=True)
    name             = db.Column(db.String(120), unique=True, nullable=False)
    calories_per_100g = db.Column(db.Float, nullable=False)
    protein_per_100g  = db.Column(db.Float, default=0.0)
    carbs_per_100g    = db.Column(db.Float, default=0.0)
    fats_per_100g     = db.Column(db.Float, default=0.0)

    food_logs = db.relationship('FoodLog', backref='food', lazy=True)

    def get_nutrients_for_quantity(self, grams):
        factor = grams / 100
        return {
            'calories': round(self.calories_per_100g * factor, 1),
            'protein':  round(self.protein_per_100g  * factor, 1),
            'carbs':    round(self.carbs_per_100g    * factor, 1),
            'fats':     round(self.fats_per_100g     * factor, 1),
        }


# ── FoodLog ──────────────────────────────────────────────────
class FoodLog(db.Model):
    __tablename__ = 'food_logs'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    food_id    = db.Column(db.Integer, db.ForeignKey('foods.id'), nullable=True)
    food_name  = db.Column(db.String(120), nullable=False)
    quantity   = db.Column(db.Float, default=100.0)
    calories   = db.Column(db.Float, default=0.0)
    protein    = db.Column(db.Float, default=0.0)
    carbs      = db.Column(db.Float, default=0.0)
    fats       = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ── Reward ───────────────────────────────────────────────────
class Reward(db.Model):
    __tablename__ = 'rewards'

    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(100), nullable=False)
    points_required = db.Column(db.Integer, nullable=False)
    is_active       = db.Column(db.Boolean, default=True)


# ── UserStats ────────────────────────────────────────────────
class UserStats(db.Model):
    __tablename__ = 'user_stats'

    user_id       = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    points        = db.Column(db.Integer, default=0)
    streak        = db.Column(db.Integer, default=0)
    last_log_date = db.Column(db.Date, nullable=True)

    def update_streak_and_points(self, points_to_add=10):
        today = date.today()
        if self.last_log_date:
            delta = (today - self.last_log_date).days
            if delta == 1:
                self.streak += 1
            elif delta > 1:
                self.streak = 1
            # delta == 0 → same day, no streak change
        else:
            self.streak = 1
        self.last_log_date = today
        self.points = (self.points or 0) + points_to_add
