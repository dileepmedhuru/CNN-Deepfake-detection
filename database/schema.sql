-- Drop tables if they exist
DROP TABLE IF EXISTS detection_history;
DROP TABLE IF EXISTS users;

-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user', -- 'user' or 'admin'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Detection history table
CREATE TABLE detection_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(20) NOT NULL, -- 'image' or 'video'
    file_path VARCHAR(500),
    prediction VARCHAR(20) NOT NULL, -- 'real' or 'fake'
    confidence FLOAT NOT NULL,
    processing_time FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_detection_user_id ON detection_history(user_id);
CREATE INDEX idx_detection_created_at ON detection_history(created_at);

-- Note: Admin user should be created via Python using proper password hashing
-- Run: python -c "from backend.app import create_app; from backend.models.user import User; from backend.database import db; app = create_app(); app.app_context().push(); admin = User(name='Admin', email='admin@deepfake.com', role='admin'); admin.set_password('admin123'); db.session.add(admin); db.session.commit()"