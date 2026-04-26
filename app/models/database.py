"""
Database Configuration
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    """User Model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    
    # Health Profile
    height = db.Column(db.Float, nullable=False)  # in cm
    weight = db.Column(db.Float, nullable=False)  # in kg
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)  # Male/Female/Other
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    suggestions = db.relationship('HealthSuggestion', backref='user', lazy=True, cascade='all, delete-orphan')
    food_logs = db.relationship('FoodLog', backref='user', lazy=True, cascade='all, delete-orphan')
    hydration_logs = db.relationship('HydrationLog', backref='user', lazy=True, cascade='all, delete-orphan')
    rewards = db.relationship('Reward', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'


class HealthSuggestion(db.Model):
    """Health Suggestion Model - Stores BMI and diet recommendations"""
    __tablename__ = 'health_suggestions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    bmi = db.Column(db.Float, nullable=False)
    bmi_category = db.Column(db.String(50), nullable=False)  # Underweight/Normal/Overweight/Obese
    suggested_diet = db.Column(db.String(50), nullable=False)  # Bulking/Cutting/Maintenance
    chosen_diet = db.Column(db.String(50), nullable=False)  # User's choice
    
    # Daily targets based on chosen diet
    calorie_target = db.Column(db.Integer, nullable=False)
    protein_target = db.Column(db.Integer, nullable=False)
    carbs_target = db.Column(db.Integer, nullable=False)
    fats_target = db.Column(db.Integer, nullable=False)
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<HealthSuggestion User:{self.user_id} BMI:{self.bmi}>'


class FoodLog(db.Model):
    """Food Log Model - Stores daily food intake"""
    __tablename__ = 'food_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    food_name = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Float, nullable=False)  # in grams
    
    # Nutritional values per 100g
    calories = db.Column(db.Float, nullable=False)
    protein = db.Column(db.Float, nullable=False)
    carbs = db.Column(db.Float, nullable=False)
    fats = db.Column(db.Float, nullable=False)
    
    # Total values (calculated)
    total_calories = db.Column(db.Float, nullable=False)
    total_protein = db.Column(db.Float, nullable=False)
    total_carbs = db.Column(db.Float, nullable=False)
    total_fats = db.Column(db.Float, nullable=False)
    
    log_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<FoodLog {self.food_name} - {self.quantity}g>'


class HydrationLog(db.Model):
    """Hydration Log Model - Tracks water intake"""
    __tablename__ = 'hydration_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    water_intake = db.Column(db.Float, nullable=False)  # in ml
    target_intake = db.Column(db.Float, nullable=False)  # in ml
    
    log_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<HydrationLog {self.water_intake}ml on {self.log_date}>'


class Reward(db.Model):
    """Reward Model - Gamification points and streaks"""
    __tablename__ = 'rewards'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    total_points = db.Column(db.Integer, default=0)
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    last_log_date = db.Column(db.Date, nullable=True)
    
    # Achievement badges (stored as comma-separated string)
    badges = db.Column(db.Text, default='')
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Reward User:{self.user_id} Points:{self.total_points}>'
