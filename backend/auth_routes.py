from flask import Blueprint, request, jsonify
from database import db
from models import User
import jwt
from datetime import datetime, timedelta
from config import Config

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def create_token(user_id):
    """Create JWT token"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=30)
    }
    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """User signup - Simple version"""
    try:
        data = request.get_json()
        
        full_name = data.get('full_name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')  # Plain text password
        
        # Validate input
        if not full_name or not email or not password:
            return jsonify({'error': 'All fields are required'}), 400
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create new user
        new_user = User(
            full_name=full_name,
            email=email,
            password=password,  # Store plain text password
            is_admin=False,
            is_verified=True
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Create token
        token = create_token(new_user.id)
        
        return jsonify({
            'message': 'Registration successful',
            'token': token,
            'user': new_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login - Simple version"""
    try:
        data = request.get_json()
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Check password (simple comparison - no hashing)
        if user.password != password:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Update last login
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Create token
        token = create_token(user.id)
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/verify-token', methods=['GET'])
def verify_token():
    """Verify JWT token"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        try:
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            user = User.query.get(payload['user_id'])
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            return jsonify({
                'valid': True,
                'user': user.to_dict()
            }), 200
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500