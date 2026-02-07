"""
SIMPLIFIED Setup Script - Initialize Database and Create Users
NO PASSWORD HASHING - Simple plain text storage
"""

import os
import sys
import sqlite3

def setup_database():
    """Set up database and create initial users"""
    
    print("=" * 60)
    print("DEEPFAKE DETECTION - SIMPLIFIED DATABASE SETUP")
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
    schema_path = 'database/schema.sql'
    
    if not os.path.exists(schema_path):
        print(f"   ✗ Error: Schema file not found at {schema_path}")
        return False
    
    # Read and execute schema
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    with open(schema_path, 'r') as f:
        schema = f.read()
        cursor.executescript(schema)
    
    connection.commit()
    print("   ✓ Database schema created")
    
    # Step 4: Verify users were created
    print("\n3. Verifying default users...")
    
    cursor.execute("SELECT email, password, role FROM users")
    users = cursor.fetchall()
    
    for email, password, role in users:
        print(f"   ✓ {role.upper()}: {email} (password: {password})")
    
    connection.close()
    
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
    print("\n⚠️  WARNING: Passwords are stored in PLAIN TEXT (no hashing)")
    print("   This is for development/demo purposes ONLY!")
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