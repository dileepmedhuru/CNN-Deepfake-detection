-- Users table (Simple - stores plain text passwords)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,  -- Plain text password (NO hashing)
    is_admin BOOLEAN DEFAULT 0,
    is_verified BOOLEAN DEFAULT 1,  -- Auto-verified
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Detection history table
CREATE TABLE IF NOT EXISTS detection_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    file_name TEXT NOT NULL,
    file_type TEXT NOT NULL,  -- 'image' or 'video'
    file_path TEXT NOT NULL,
    result TEXT NOT NULL,  -- 'real' or 'fake'
    confidence REAL NOT NULL,
    processing_time REAL NOT NULL,
    metadata TEXT,  -- JSON string with additional info
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create default admin user
INSERT OR IGNORE INTO users (id, full_name, email, password, is_admin) 
VALUES (1, 'Admin', 'admin@deepfake.com', 'admin123', 1);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_detection_user_id ON detection_history(user_id);
CREATE INDEX IF NOT EXISTS idx_detection_created_at ON detection_history(created_at);