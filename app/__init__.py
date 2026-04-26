"""
SNTS — App Factory
Initialises Flask, SQLAlchemy, Flask-Login and registers all blueprints.
"""

import os
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'snts-secret-2024-xKj9')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(
        app.instance_path, 'snts.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    # Blueprints
    from app.blueprints.auth.routes  import auth_bp
    from app.blueprints.user.routes  import user_bp
    from app.blueprints.admin.routes import admin_bp
    from app.blueprints.utils.routes import utils_bp

    app.register_blueprint(auth_bp,  url_prefix='/auth')
    app.register_blueprint(user_bp,  url_prefix='/user')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(utils_bp, url_prefix='/utils')

    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template
        return render_template('shared/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        from flask import render_template
        return render_template('shared/500.html'), 500

    with app.app_context():
        db.create_all()
        _seed_initial_data()

    return app


def _seed_initial_data():
    from app.models.models import User, Food, Reward, UserStats
    from werkzeug.security import generate_password_hash

    # Admin user
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin', email='admin@snts.com',
            password_hash=generate_password_hash('admin123'),
            height=175.0, weight=70.0, age=30, gender='male',
            activity_level='moderate', role='admin',
            bmi=22.9, diet_type='maintenance'
        )
        db.session.add(admin)
        db.session.flush()  # get admin.id
        db.session.add(UserStats(user_id=admin.id, points=0, streak=0))
        db.session.commit()

    # Indian foods
    foods_data = [
        # (name, cal, prot, carbs, fats)
        ('Steamed Rice',          130, 2.7,  28.2, 0.3),
        ('Brown Rice',            111, 2.6,  23.0, 0.9),
        ('Roti (Wheat Chapati)',  297, 9.0,  52.9, 5.5),
        ('Poha (Flattened Rice)', 130, 2.5,  27.0, 0.5),
        ('Idli',                   58, 2.0,  12.0, 0.1),
        ('Dosa',                  165, 3.9,  28.0, 4.7),
        ('Upma',                  153, 4.0,  26.0, 4.0),
        ('Dal (Cooked Lentils)',   93, 6.3,  15.6, 0.4),
        ('Dal Makhani',           155, 8.0,  18.0, 6.0),
        ('Chole (Chickpea Curry)',163, 8.0,  20.0, 5.5),
        ('Rajma Curry',           155, 8.5,  22.0, 3.5),
        ('Sambar',                 55, 3.0,   8.0, 1.2),
        ('Paneer',                265,18.3,   1.2,20.8),
        ('Palak Paneer',          183,10.0,   7.0,13.0),
        ('Shahi Paneer',          245,12.0,  10.0,18.0),
        ('Paneer Tikka',          220,15.0,   6.0,15.0),
        ('Aloo Paratha',          300, 7.0,  48.0, 9.0),
        ('Aloo Sabzi',             97, 2.3,  16.0, 3.0),
        ('Aloo Gobi',              85, 2.5,  13.0, 2.5),
        ('Bhindi Masala',          83, 2.0,  10.0, 4.0),
        ('Baingan Bharta',         75, 2.0,  10.0, 3.0),
        ('Chicken Curry',         180,18.0,   6.0, 9.0),
        ('Butter Chicken',        230,22.0,   8.0,12.0),
        ('Tandoori Chicken',      160,25.0,   2.0, 5.0),
        ('Chicken Biryani',       200,12.0,  25.0, 5.5),
        ('Chicken Tikka Masala',  220,23.0,   9.0,10.0),
        ('Egg Curry',             180,13.0,   4.0,12.0),
        ('Boiled Egg',            155,13.0,   1.1,11.0),
        ('Scrambled Egg',         148,10.0,   1.4,11.5),
        ('Fish Curry',            150,20.0,   5.0, 5.5),
        ('Mutton Curry',          250,20.0,   4.0,17.0),
        ('Vegetable Pulao',       165, 4.0,  30.0, 3.5),
        ('Jeera Rice',            155, 3.0,  30.0, 3.0),
        ('Curd (Plain Yogurt)',    61, 3.5,   4.7, 3.3),
        ('Raita',                  60, 2.5,   5.0, 2.8),
        ('Lassi (Plain)',          98, 3.5,  13.0, 3.5),
        ('Milk (Full Fat)',        61, 3.2,   4.8, 3.3),
        ('Masala Chai (with milk)',47, 1.6,   6.0, 1.8),
        ('Samosa (1 piece ~50g)', 262, 4.0,  33.0,13.0),
        ('Pakora (Vegetable)',    318, 6.0,  35.0,17.0),
        ('Pani Puri (1 piece)',    35, 0.7,   6.0, 1.0),
        ('Dhokla',                160, 5.0,  27.0, 3.5),
        ('Khichdi',               105, 4.5,  20.0, 1.5),
        ('Pongal',                180, 4.0,  30.0, 5.0),
        ('Appam',                 120, 2.5,  25.0, 0.5),
        ('Halwa (Suji)',          360, 4.5,  55.0,13.0),
        ('Kheer (Rice Pudding)',  150, 4.0,  26.0, 3.5),
        ('Gulab Jamun (1 piece)', 150, 2.5,  27.0, 4.5),
    ]

    for name, cal, prot, carbs, fats in foods_data:
        if not Food.query.filter_by(name=name).first():
            db.session.add(Food(
                name=name,
                calories_per_100g=cal,
                protein_per_100g=prot,
                carbs_per_100g=carbs,
                fats_per_100g=fats
            ))

    # Rewards
    rewards_data = [
        ('First Log Badge',    50,  True),
        ('Week Warrior',      100,  True),
        ('Nutrition Explorer', 200, True),
        ('Consistency King',  500,  True),
        ('Elite Tracker',    1000,  True),
    ]
    for name, pts, active in rewards_data:
        if not Reward.query.filter_by(name=name).first():
            db.session.add(Reward(name=name, points_required=pts, is_active=active))

    db.session.commit()
