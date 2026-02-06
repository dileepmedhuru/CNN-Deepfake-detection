from flask import Blueprint, request, jsonify, session, current_app
from models.detection import DetectionHistory
from database import db
from utils.security import login_required
from utils.validators import allowed_file
from utils.file_handler import save_uploaded_file
from utils.video_processor import extract_frames, preprocess_frame
from utils.model_utils import load_trained_model, predict_single, aggregate_video_predictions
import time
import cv2
import numpy as np
import os

detection_bp = Blueprint('detection', __name__, url_prefix='/api/detection')

# Load model once at startup
MODEL = None

def get_model():
    """Get or load the ML model"""
    global MODEL
    if MODEL is None:
        model_path = current_app.config['MODEL_PATH']
        MODEL, error = load_trained_model(model_path)
        if error:
            print(f"Warning: Could not load model - {error}")
    return MODEL

@detection_bp.route('/upload', methods=['POST'])
@login_required
def upload_and_detect():
    """Upload and analyze image or video"""
    try:
        start_time = time.time()
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Determine file type
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        
        if file_extension in current_app.config['ALLOWED_IMAGE_EXTENSIONS']:
            file_type = 'image'
        elif file_extension in current_app.config['ALLOWED_VIDEO_EXTENSIONS']:
            file_type = 'video'
        else:
            return jsonify({'error': 'Invalid file type. Allowed: images and videos'}), 400
        
        # Check if allowed
        allowed_extensions = current_app.config['ALLOWED_IMAGE_EXTENSIONS'] | current_app.config['ALLOWED_VIDEO_EXTENSIONS']
        if not allowed_file(file.filename, allowed_extensions):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Save file
        success, file_path, original_filename = save_uploaded_file(file, file_type)
        if not success:
            return jsonify({'error': f'Failed to save file: {file_path}'}), 500
        
        # Load model
        model = get_model()
        if model is None:
            return jsonify({
                'error': 'Model not trained yet',
                'prediction': 'unknown',
                'confidence': 0,
                'message': 'Please train the model first'
            }), 200
        
        # Perform detection
        if file_type == 'image':
            prediction, confidence = detect_image(model, file_path)
        else:
            prediction, confidence = detect_video(model, file_path)
        
        processing_time = time.time() - start_time
        
        # Save to history
        history_entry = DetectionHistory(
            user_id=session['user_id'],
            file_name=original_filename,
            file_type=file_type,
            file_path=file_path,
            prediction=prediction,
            confidence=confidence,
            processing_time=processing_time
        )
        db.session.add(history_entry)
        db.session.commit()
        
        return jsonify({
            'message': 'Detection completed',
            'detection': history_entry.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Server error: {str(e)}'}), 500

def detect_image(model, image_path):
    """Detect deepfake in image"""
    try:
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            return 'error', 0.0
        
        # Preprocess
        processed_image = preprocess_frame(image, target_size=(224, 224))
        
        # Predict
        prediction, confidence = predict_single(model, processed_image)
        
        return prediction, confidence
    
    except Exception as e:
        print(f"Error in image detection: {e}")
        return 'error', 0.0

def detect_video(model, video_path, num_frames=10):
    """Detect deepfake in video"""
    try:
        # Extract frames
        frames, error = extract_frames(video_path, num_frames=num_frames)
        if error or not frames:
            return 'error', 0.0
        
        # Analyze each frame
        frame_predictions = []
        for frame in frames:
            processed_frame = preprocess_frame(frame, target_size=(224, 224))
            prediction, confidence = predict_single(model, processed_frame)
            frame_predictions.append((prediction, confidence))
        
        # Aggregate predictions
        final_prediction, avg_confidence = aggregate_video_predictions(frame_predictions)
        
        return final_prediction, avg_confidence
    
    except Exception as e:
        print(f"Error in video detection: {e}")
        return 'error', 0.0

@detection_bp.route('/history', methods=['GET'])
@login_required
def get_history():
    """Get detection history for current user"""
    try:
        user_id = session['user_id']
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Query history
        history_query = DetectionHistory.query.filter_by(user_id=user_id).order_by(
            DetectionHistory.created_at.desc()
        )
        
        paginated = history_query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'history': [item.to_dict() for item in paginated.items],
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': page
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@detection_bp.route('/history/<int:detection_id>', methods=['GET'])
@login_required
def get_detection_detail(detection_id):
    """Get specific detection detail"""
    try:
        user_id = session['user_id']
        
        detection = DetectionHistory.query.filter_by(
            id=detection_id,
            user_id=user_id
        ).first()
        
        if not detection:
            return jsonify({'error': 'Detection not found'}), 404
        
        return jsonify({'detection': detection.to_dict()}), 200
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@detection_bp.route('/stats', methods=['GET'])
@login_required
def get_user_stats():
    """Get user detection statistics"""
    try:
        user_id = session['user_id']
        
        total = DetectionHistory.query.filter_by(user_id=user_id).count()
        fake_count = DetectionHistory.query.filter_by(user_id=user_id, prediction='fake').count()
        real_count = DetectionHistory.query.filter_by(user_id=user_id, prediction='real').count()
        
        return jsonify({
            'total_detections': total,
            'fake_detected': fake_count,
            'real_detected': real_count
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500