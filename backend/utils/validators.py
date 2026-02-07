"""
SIMPLIFIED Validators - Basic validation only
"""
import re

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """
    SIMPLIFIED password validation
    Just check minimum length
    """
    if len(password) < 3:
        return False, "Password must be at least 3 characters long"
    
    return True, "Valid password"

def validate_name(name):
    """Validate name"""
    if not name or len(name.strip()) < 2:
        return False, "Name must be at least 2 characters"
    
    if len(name) > 100:
        return False, "Name must be less than 100 characters"
    
    return True, "Valid name"

def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def sanitize_filename(filename):
    """Basic filename sanitization"""
    # Remove any path components
    filename = filename.replace('/', '_').replace('\\', '_')
    # Remove any potentially dangerous characters
    filename = re.sub(r'[<>:"|?*]', '_', filename)
    return filename

def validate_file_size(file, max_size_mb=100):
    """Validate file size"""
    file.seek(0, 2)  # Seek to end
    size = file.tell()
    file.seek(0)  # Reset to beginning
    
    max_size_bytes = max_size_mb * 1024 * 1024
    return size <= max_size_bytes, size