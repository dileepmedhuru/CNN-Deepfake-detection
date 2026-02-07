"""
Easy Setup Script for Deepfake Detection System
Run this to initialize everything
"""

import os
import sys

def setup():
    print("=" * 60)
    print("DEEPFAKE DETECTION SYSTEM - SETUP")
    print("=" * 60)
    
    # Step 1: Check Python version
    print("\n1. Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Step 2: Create directories
    print("\n2. Creating directories...")
    directories = [
        'database',
        'backend/uploads/images',
        'backend/uploads/videos',
        'ml_models'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"   ✅ {directory}")
    
    # Step 3: Initialize database
    print("\n3. Initializing database...")
    try:
        sys.path.insert(0, 'backend')
        from database import init_db
        init_db('database/deepfake.db', 'database/schema.sql')
        print("   ✅ Database initialized")
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ SETUP COMPLETE!")
    print("=" * 60)
    print("\n📋 Next Steps:")
    print("   1. Install dependencies: cd backend && pip install -r requirements.txt")
    print("   2. Run application: python app.py")
    print("   3. Open browser: http://localhost:5000")
    print("\n👤 Default Admin:")
    print("   Email: admin@deepfake.com")
    print("   Password: admin123")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = setup()
    sys.exit(0 if success else 1)
    