"""
Authentication Routes
Login, Registration, and Session Management
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User, HealthSuggestion, Reward
from app.utils import calculate_bmi, get_bmi_category, suggest_diet_type, calculate_diet_targets, calculate_water_intake
from functools import wraps

auth_bp = Blueprint('auth', __name__)


def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Login required'}), 401
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/')
def index():
    """Landing page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard.dashboard'))
    return render_template('index.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and handler"""
    if request.method == 'GET':
        if 'user_id' in session:
            return redirect(url_for('dashboard.dashboard'))
        return render_template('login.html')
    
    # POST request - handle login
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not check_password_hash(user.password, password):
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    
    # Set session
    session['user_id'] = user.id
    session['username'] = user.username
    
    return jsonify({
        'success': True, 
        'message': 'Login successful',
        'redirect': url_for('dashboard.dashboard')
    })


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page and handler"""
    if request.method == 'GET':
        if 'user_id' in session:
            return redirect(url_for('dashboard.dashboard'))
        return render_template('register.html')
    
    # POST request - handle registration
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['username', 'email', 'password', 'height', 'weight', 'age', 'gender']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'success': False, 'message': f'{field.title()} is required'}), 400
    
    # Check if username or email already exists
    existing_user = User.query.filter(
        (User.username == data['username']) | (User.email == data['email'])
    ).first()
    
    if existing_user:
        return jsonify({'success': False, 'message': 'Username or email already exists'}), 400
    
    try:
        # Create new user
        new_user = User(
            username=data['username'],
            email=data['email'],
            password=generate_password_hash(data['password']),
            height=float(data['height']),
            weight=float(data['weight']),
            age=int(data['age']),
            gender=data['gender']
        )
        
        db.session.add(new_user)
        db.session.flush()  # Get user ID
        
        # Calculate health metrics
        bmi = calculate_bmi(new_user.weight, new_user.height)
        bmi_category = get_bmi_category(bmi)
        suggested_diet = suggest_diet_type(bmi, bmi_category)
        
        # Calculate diet targets
        targets = calculate_diet_targets(
            new_user.weight, 
            new_user.height, 
            new_user.age, 
            new_user.gender,
            suggested_diet
        )
        
        # Create health suggestion
        health_suggestion = HealthSuggestion(
            user_id=new_user.id,
            bmi=bmi,
            bmi_category=bmi_category,
            suggested_diet=suggested_diet,
            chosen_diet=suggested_diet,  # Default to suggested
            calorie_target=targets['calorie_target'],
            protein_target=targets['protein_target'],
            carbs_target=targets['carbs_target'],
            fats_target=targets['fats_target']
        )
        
        # Initialize reward system
        reward = Reward(user_id=new_user.id)
        
        db.session.add(health_suggestion)
        db.session.add(reward)
        db.session.commit()
        
        # Set session
        session['user_id'] = new_user.id
        session['username'] = new_user.username
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'redirect': url_for('dashboard.dashboard'),
            'health_data': {
                'bmi': bmi,
                'bmi_category': bmi_category,
                'suggested_diet': suggested_diet,
                'targets': targets
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Registration failed: {str(e)}'}), 500


@auth_bp.route('/logout')
def logout():
    """Logout handler"""
    session.clear()
    return redirect(url_for('auth.index'))


@auth_bp.route('/check-session')
def check_session():
    """Check if user is logged in"""
    if 'user_id' in session:
        return jsonify({
            'logged_in': True,
            'user_id': session['user_id'],
            'username': session['username']
        })
    return jsonify({'logged_in': False})
