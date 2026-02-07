from flask import Blueprint, request, jsonify
from database import db
from models import User, Detection
from utils import verify_token
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

def verify_admin():
    """Verify user is admin"""
    user = verify_token()
    if not user or not user.is_admin:
        return None
    return user

@admin_bp.route('/users', methods=['GET'])
def get_all_users():
    """Get all users (admin only)"""
    admin = verify_admin()
    if not admin:
        return jsonify({'error': 'Unauthorized - Admin access required'}), 403
    
    try:
        users = User.query.all()
        
        # Include detection count for each user
        users_data = []
        for user in users:
            user_dict = user.to_dict()
            user_dict['detection_count'] = Detection.query.filter_by(user_id=user.id).count()
            users_data.append(user_dict)
        
        return jsonify({
            'users': users_data
        }), 200
        
    except Exception as e:
        print(f"Error in get_all_users: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_detail(user_id):
    """Get detailed user information (admin only)"""
    admin = verify_admin()
    if not admin:
        return jsonify({'error': 'Unauthorized - Admin access required'}), 403
    
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user detections
        detections = Detection.query.filter_by(user_id=user_id).all()
        
        user_data = user.to_dict()
        user_data['detections'] = [d.to_dict() for d in detections]
        user_data['detection_count'] = len(detections)
        
        return jsonify({
            'user': user_data
        }), 200
        
    except Exception as e:
        print(f"Error in get_user_detail: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/detections', methods=['GET'])
def get_all_detections():
    """Get all detections from all users (admin only)"""
    admin = verify_admin()
    if not admin:
        return jsonify({'error': 'Unauthorized - Admin access required'}), 403
    
    try:
        # Join with users to get user names
        detections = db.session.query(
            Detection,
            User.full_name,
            User.email
        ).join(User, Detection.user_id == User.id)\
         .order_by(Detection.created_at.desc())\
         .all()
        
        detections_data = []
        for detection, full_name, email in detections:
            det_dict = detection.to_dict()
            det_dict['full_name'] = full_name
            det_dict['email'] = email
            detections_data.append(det_dict)
        
        return jsonify({
            'detections': detections_data
        }), 200
        
    except Exception as e:
        print(f"Error in get_all_detections: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/stats', methods=['GET'])
def get_admin_stats():
    """Get system-wide statistics (admin only)"""
    admin = verify_admin()
    if not admin:
        return jsonify({'error': 'Unauthorized - Admin access required'}), 403
    
    try:
        total_users = User.query.count()
        total_detections = Detection.query.count()
        fake_detections = Detection.query.filter_by(result='fake').count()
        real_detections = Detection.query.filter_by(result='real').count()
        
        return jsonify({
            'total_users': total_users,
            'total_detections': total_detections,
            'fake_detections': fake_detections,
            'real_detections': real_detections
        }), 200
        
    except Exception as e:
        print(f"Error in get_admin_stats: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/dashboard-stats', methods=['GET'])
def get_dashboard_stats():
    """Get comprehensive dashboard statistics (admin only)"""
    admin = verify_admin()
    if not admin:
        return jsonify({'error': 'Unauthorized - Admin access required'}), 403
    
    try:
        total_users = User.query.count()
        total_detections = Detection.query.count()
        fake_detections = Detection.query.filter_by(result='fake').count()
        real_detections = Detection.query.filter_by(result='real').count()
        
        return jsonify({
            'total_users': total_users,
            'total_detections': total_detections,
            'fake_detections': fake_detections,
            'real_detections': real_detections
        }), 200
        
    except Exception as e:
        print(f"Error in get_dashboard_stats: {e}")
        return jsonify({'error': str(e)}), 500