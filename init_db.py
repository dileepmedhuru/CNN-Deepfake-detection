# init_db.py
from backend.database import init_db

if __name__ == "__main__":
    init_db('database/deepfake.db', 'database/schema.sql')
    print("Database initialized successfully!")