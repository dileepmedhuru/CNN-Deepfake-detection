from flask import Blueprint, request, jsonify
from models.user import User
from models.detection import DetectionHistory
from database import db
from utils.security import admin_required
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_all_users():
    """Get all users (admin only)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        users_query = User.query.order_by(User.created_at.desc())
        paginated = users_query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'users': [user.to_dict() for user in paginated.items],
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': page
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user_detail(user_id):
    """Get specific user details"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user's detection count
        detection_count = DetectionHistory.query.filter_by(user_id=user_id).count()
        
        user_data = user.to_dict()
        user_data['detection_count'] = detection_count
        
        return jsonify({'user': user_data}), 200
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete a user"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Prevent deleting admin
        if user.role == 'admin':
            return jsonify({'error': 'Cannot delete admin user'}), 403
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'User deleted successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@admin_bp.route('/users/<int:user_id>/toggle-role', methods=['PUT'])
@admin_required
def toggle_user_role(user_id):
    """Toggle user role between user and admin"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Toggle role
        user.role = 'admin' if user.role == 'user' else 'user'
        db.session.commit()
        
        return jsonify({
            'message': 'User role updated',
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@admin_bp.route('/detections', methods=['GET'])
@admin_required
def get_all_detections():
    """Get all detection history (admin only)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        detections_query = DetectionHistory.query.order_by(
            DetectionHistory.created_at.desc()
        )
        paginated = detections_query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Get detection data with user info
        detections_data = []
        for detection in paginated.items:
            det_dict = detection.to_dict()
            user = User.query.get(detection.user_id)
            det_dict['user_name'] = user.name if user else 'Unknown'
            det_dict['user_email'] = user.email if user else 'Unknown'
            detections_data.append(det_dict)
        
        return jsonify({
            'detections': detections_data,
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': page
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@admin_bp.route('/stats', methods=['GET'])
@admin_required
def get_system_stats():
    """Get system-wide statistics"""
    try:
        # User statistics
        total_users = User.query.count()
        admin_count = User.query.filter_by(role='admin').count()
        user_count = User.query.filter_by(role='user').count()
        
        # Detection statistics
        total_detections = DetectionHistory.query.count()
        fake_count = DetectionHistory.query.filter_by(prediction='fake').count()
        real_count = DetectionHistory.query.filter_by(prediction='real').count()
        image_count = DetectionHistory.query.filter_by(file_type='image').count()
        video_count = DetectionHistory.query.filter_by(file_type='video').count()
        
        # Average confidence
        avg_confidence = db.session.query(
            func.avg(DetectionHistory.confidence)
        ).scalar() or 0
        
        # Recent activity (last 7 days)
        from datetime import datetime, timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_detections = DetectionHistory.query.filter(
            DetectionHistory.created_at >= week_ago
        ).count()
        
        return jsonify({
            'users': {
                'total': total_users,
                'admins': admin_count,
                'regular_users': user_count
            },
            'detections': {
                'total': total_detections,
                'fake': fake_count,
                'real': real_count,
                'images': image_count,
                'videos': video_count,
                'avg_confidence': round(avg_confidence, 2),
                'recent_week': recent_detections
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@admin_bp.route('/detections/<int:detection_id>', methods=['DELETE'])
@admin_required
def delete_detection(detection_id):
    """Delete a detection record"""
    try:
        detection = DetectionHistory.query.get(detection_id)
        if not detection:
            return jsonify({'error': 'Detection not found'}), 404
        
        db.session.delete(detection)
        db.session.commit()
        
        return jsonify({'message': 'Detection deleted successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Server error: {str(e)}'}), 500