from flask import Flask, send_from_directory, session
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
    
    # Configure CORS with credentials support
    CORS(app, 
         supports_credentials=True, 
         origins=['http://localhost:5000', 'http://127.0.0.1:5000'],
         allow_headers=['Content-Type'],
         expose_headers=['Content-Type'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    
    # Configure session
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SECURE'] = False  # Set to True if using HTTPS
    
    # Register blueprints
    from routes import auth_bp, detection_bp, admin_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(detection_bp)
    app.register_blueprint(admin_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        print("Database tables created successfully")
    
    # Serve frontend files
    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')
    
    @app.route('/<path:path>')
    def serve_static(path):
        if os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, 'index.html')
    
    # Health check endpoint
    @app.route('/api/health')
    def health():
        return {'status': 'ok', 'message': 'Server is running'}
    
    return app

if __name__ == '__main__':
    app = create_app('development')
    app.run(host='0.0.0.0', port=5000, debug=True)