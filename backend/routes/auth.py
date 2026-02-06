from flask import Blueprint, request, jsonify, session
from models.user import User
from database import db
from utils.validators import validate_email, validate_password, validate_name
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """User signup endpoint"""
    try:
        data = request.get_json()
        
        # Validate input
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Validate name
        is_valid, msg = validate_name(name)
        if not is_valid:
            return jsonify({'error': msg}), 400
        
        # Validate email
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password
        is_valid, msg = validate_password(password)
        if not is_valid:
            return jsonify({'error': msg}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create new user
        new_user = User(name=name, email=email)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        # Auto login after signup
        session['user_id'] = new_user.id
        session['user_name'] = new_user.name
        session['user_email'] = new_user.email
        session['user_role'] = new_user.role
        
        return jsonify({
            'message': 'Account created successfully',
            'user': new_user.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Create session
        session['user_id'] = user.id
        session['user_name'] = user.name
        session['user_email'] = user.email
        session['user_role'] = user.role
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@auth_bp.route('/admin-login', methods=['POST'])
def admin_login():
    """Admin login endpoint"""
    try:
        data = request.get_json()
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check if admin
        if user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Create session
        session['user_id'] = user.id
        session['user_name'] = user.name
        session['user_email'] = user.email
        session['user_role'] = user.role
        
        return jsonify({
            'message': 'Admin login successful',
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout endpoint"""
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Get current user info"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': user.to_dict()}), 200

@auth_bp.route('/check-session', methods=['GET'])
def check_session():
    """Check if user is logged in"""
    if 'user_id' in session:
        return jsonify({
            'logged_in': True,
            'user_id': session['user_id'],
            'user_name': session.get('user_name'),
            'user_role': session.get('user_role')
        }), 200
    else:
        return jsonify({'logged_in': False}), 200