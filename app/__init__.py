"""
Flask Application Factory
Main application initialization and configuration
"""
import os
from flask import Flask
from dotenv import load_dotenv
from app.models import db
from app.routes import auth_bp, dashboard_bp, food_bp, health_bp, history_bp, rewards_bp

# Load environment variables
load_dotenv()


def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_secret_key_snts_2024')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///snts.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(food_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(rewards_bp)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app
