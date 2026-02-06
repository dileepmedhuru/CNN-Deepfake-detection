from functools import wraps
from flask import session, redirect, url_for, jsonify, request
from models.user import User

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # If AJAX request, return JSON error
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'Authentication required', 'redirect': '/login.html'}), 401
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'Authentication required', 'redirect': '/admin-login.html'}), 401
            return redirect('/admin-login.html')
        
        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'Admin access required'}), 403
            return redirect('/index.html')
        
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get current logged-in user"""
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

def is_logged_in():
    """Check if user is logged in"""
    return 'user_id' in session

def is_admin():
    """Check if current user is admin"""
    user = get_current_user()
    return user and user.role == 'admin'