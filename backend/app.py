from flask import Flask, send_from_directory
from flask_cors import CORS
from config import config
from database import db
import os

def create_app(config_name='development'):
    """Create and configure Flask app"""
    app = Flask(__name__, 
                static_folder='../frontend',
                static_url_path='')
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)  # Enable CORS for all routes
    
    # Create necessary directories
    os.makedirs('uploads/images', exist_ok=True)
    os.makedirs('uploads/videos', exist_ok=True)
    
    # Register blueprints
    try:
        from auth_routes import auth_bp
        app.register_blueprint(auth_bp)
        print("✓ Auth routes registered")
    except Exception as e:
        print(f"✗ Error registering auth routes: {e}")
    
    try:
        from detection_routes import detection_bp
        app.register_blueprint(detection_bp)
        print("✓ Detection routes registered")
    except Exception as e:
        print(f"✗ Error registering detection routes: {e}")
    
    try:
        from admin_routes import admin_bp
        app.register_blueprint(admin_bp)
        print("✓ Admin routes registered")
    except Exception as e:
        print(f"✗ Error registering admin routes: {e}")
    
    # Create database tables
    with app.app_context():
        try:
            db.create_all()
            print("✓ Database tables created successfully")
        except Exception as e:
            print(f"✗ Database error: {e}")
    
    # Serve frontend files
    @app.route('/')
    def index():
        return send_from_directory('../frontend', 'index.html')
    
    @app.route('/<path:path>')
    def serve_static(path):
        if os.path.exists(os.path.join('../frontend', path)):
            return send_from_directory('../frontend', path)
        return send_from_directory('../frontend', 'index.html')
    
    # Health check
    @app.route('/health')
    def health():
        return {'status': 'healthy'}, 200
    
    return app

if __name__ == '__main__':
    app = create_app('development')
    print("=" * 60)
    print("🚀 Deepfake Detection System Starting...")
    print("=" * 60)
    print("📡 Server: http://localhost:5000")
    print("👤 Admin: admin@deepfake.com / admin123")
    print("📝 User:  test@example.com / test123")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)