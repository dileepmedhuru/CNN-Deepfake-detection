import os
from datetime import timedelta
from pathlib import Path

# Get the absolute path to the project root
BASE_DIR = Path(__file__).resolve().parent.parent  # Goes up from backend/ to project root

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-12345'
    
    # Database path - absolute path to database/deepfake.db
    DATABASE_PATH = BASE_DIR / 'database' / 'deepfake.db'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-12345'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=30)
    
    # File Upload Configuration
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file size
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv'}
    
    # Model Configuration - absolute path
    MODEL_PATH = BASE_DIR / 'ml_models' / 'cnn_model.h5'
    
    @staticmethod
    def init_app(app):
        # Ensure database directory exists
        db_dir = BASE_DIR / 'database'
        db_dir.mkdir(exist_ok=True)
        print(f"📁 Database directory: {db_dir}")
        print(f"📁 Database file: {Config.DATABASE_PATH}")

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}