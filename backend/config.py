import os
from datetime import timedelta

class Config:
    """Base configuration"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE_PATH = os.path.join(os.path.dirname(BASE_DIR), 'database', 'deepfake.db')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # File Upload
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file size
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv'}
    
    # ML Model
    MODEL_PATH = os.path.join(BASE_DIR, 'ml_models', 'cnn_model.h5')
    
    # CORS
    CORS_ORIGINS = ['http://localhost:5000', 'http://127.0.0.1:5000']
    
    @staticmethod
    def init_app(app):
        """Initialize application"""
        # Create necessary directories
        os.makedirs(os.path.join(Config.UPLOAD_FOLDER, 'images'), exist_ok=True)
        os.makedirs(os.path.join(Config.UPLOAD_FOLDER, 'videos'), exist_ok=True)
        os.makedirs(os.path.dirname(Config.MODEL_PATH), exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}