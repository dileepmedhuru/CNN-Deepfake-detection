from flask import request
from models import User
import jwt
from config import Config
import os
from werkzeug.utils import secure_filename
import uuid

def verify_token():
    """Verify JWT token and return user"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return None
        
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
        user = User.query.get(payload['user_id'])
        
        return user
        
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

def allowed_file(filename, file_type='image'):
    """Check if file extension is allowed"""
    if '.' not in filename:
        return False
    
    ext = filename.rsplit('.', 1)[1].lower()
    
    if file_type == 'image':
        return ext in Config.ALLOWED_IMAGE_EXTENSIONS
    elif file_type == 'video':
        return ext in Config.ALLOWED_VIDEO_EXTENSIONS
    
    return False

def save_upload_file(file, subfolder='images'):
    """Save uploaded file and return path"""
    # Create upload directory if it doesn't exist
    upload_dir = os.path.join(Config.UPLOAD_FOLDER, subfolder)
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Save file
    file.save(file_path)
    
    return file_path