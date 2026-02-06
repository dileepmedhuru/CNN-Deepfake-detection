import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app

def save_uploaded_file(file, file_type='image'):
    """
    Save uploaded file and return file path
    
    Args:
        file: FileStorage object from Flask
        file_type: 'image' or 'video'
    
    Returns:
        tuple: (success, file_path or error_message, original_filename)
    """
    try:
        # Get original filename
        original_filename = secure_filename(file.filename)
        
        # Generate unique filename
        file_extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_extension}"
        
        # Determine save directory
        upload_folder = current_app.config['UPLOAD_FOLDER']
        if file_type == 'image':
            save_dir = os.path.join(upload_folder, 'images')
        else:
            save_dir = os.path.join(upload_folder, 'videos')
        
        # Ensure directory exists
        os.makedirs(save_dir, exist_ok=True)
        
        # Full file path
        file_path = os.path.join(save_dir, unique_filename)
        
        # Save file
        file.save(file_path)
        
        return True, file_path, original_filename
    
    except Exception as e:
        return False, str(e), None

def delete_file(file_path):
    """Delete a file if it exists"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting file: {e}")
        return False

def get_file_info(file_path):
    """Get file information"""
    if not os.path.exists(file_path):
        return None
    
    stat = os.stat(file_path)
    return {
        'size': stat.st_size,
        'created': datetime.fromtimestamp(stat.st_ctime),
        'modified': datetime.fromtimestamp(stat.st_mtime)
    }

def cleanup_old_files(directory, days=7):
    """Clean up files older than specified days"""
    try:
        now = datetime.now()
        count = 0
        
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                file_modified = datetime.fromtimestamp(os.path.getmtime(file_path))
                if (now - file_modified).days > days:
                    os.remove(file_path)
                    count += 1
        
        return count
    except Exception as e:
        print(f"Error cleaning up files: {e}")
        return 0