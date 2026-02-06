"""
Setup Script - Initialize Database and Create Users
Run this script to set up your database properly
"""

import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def setup_database():
    """Set up database and create initial users"""
    
    print("=" * 60)
    print("DEEPFAKE DETECTION - DATABASE SETUP")
    print("=" * 60)
    
    # Step 1: Remove old database
    db_path = 'database/deepfake.db'
    if os.path.exists(db_path):
        print(f"\n1. Removing old database: {db_path}")
        os.remove(db_path)
        print("   ✓ Old database removed")
    else:
        print(f"\n1. No existing database found")
    
    # Step 2: Create database directory
    os.makedirs('database', exist_ok=True)
    
    # Step 3: Initialize database with schema
    print("\n2. Initializing database with schema...")
    from backend.database import init_db
    init_db(db_path, 'database/schema.sql')
    print("   ✓ Database schema created")
    
    # Step 4: Create users with proper password hashing
    print("\n3. Creating users...")
    from backend.app import create_app
    from backend.models.user import User
    from backend.database import db
    
    app = create_app('development')
    
    with app.app_context():
        # Create admin user
        print("   Creating admin user...")
        admin = User(
            name='Admin',
            email='admin@deepfake.com',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create test user
        print("   Creating test user...")
        test_user = User(
            name='Test User',
            email='test@example.com',
            role='user'
        )
        test_user.set_password('test123')
        db.session.add(test_user)
        
        # Commit to database
        db.session.commit()
        print("   ✓ Users created")
        
        # Verify passwords
        print("\n4. Verifying password hashes...")
        
        admin_check = User.query.filter_by(email='admin@deepfake.com').first()
        if admin_check and admin_check.check_password('admin123'):
            print("   ✓ Admin password verified")
        else:
            print("   ✗ Admin password verification FAILED!")
            return False
        
        test_check = User.query.filter_by(email='test@example.com').first()
        if test_check and test_check.check_password('test123'):
            print("   ✓ Test user password verified")
        else:
            print("   ✗ Test user password verification FAILED!")
            return False
    
    print("\n" + "=" * 60)
    print("✓ SETUP COMPLETE!")
    print("=" * 60)
    print("\nDefault Accounts Created:")
    print("\n1. Admin Account:")
    print("   Email:    admin@deepfake.com")
    print("   Password: admin123")
    print("   URL:      http://localhost:5000/admin-login.html")
    print("\n2. Test User Account:")
    print("   Email:    test@example.com")
    print("   Password: test123")
    print("   URL:      http://localhost:5000/login.html")
    print("\nNext Steps:")
    print("1. Run: cd backend")
    print("2. Run: python app.py")
    print("3. Open: http://localhost:5000")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        success = setup_database()
        if success:
            print("\n✓ Setup successful! You can now run your application.")
            sys.exit(0)
        else:
            print("\n✗ Setup failed! Check errors above.")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)