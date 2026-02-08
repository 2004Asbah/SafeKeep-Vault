"""
Database Migration: Add role column to users table if it doesn't exist
This script safely adds the 'role' column to existing users table to fix the registration 500 error.
"""
import sqlite3
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Path to the database
db_path = os.path.join(os.getcwd(), 'backend', 'safekeep.db')

def migrate_database():
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if 'role' column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'role' in column_names:
            print("✓ 'role' column already exists. No migration needed.")
            return True
        
        print("⚠️ 'role' column is missing. Adding it now...")
        
        # Add the role column with default value 'admin'
        cursor.execute("ALTER TABLE users ADD COLUMN role VARCHAR DEFAULT 'admin'")
        
        # Update existing users to have 'admin' role
        cursor.execute("UPDATE users SET role = 'admin' WHERE role IS NULL")
        
        conn.commit()
        print("✓ Successfully added 'role' column to users table")
        print("✓ All existing users have been set to 'admin' role")
        
        # Verify the change
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        print("\nUpdated users table schema:")
        print(f"{'Name':<20} {'Type':<15} {'Default':<15}")
        print("-" * 50)
        for col in columns:
            _, name, type_, _, default, _ = col
            print(f"{name:<20} {type_:<15} {str(default):<15}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("Starting database migration...\n")
    success = migrate_database()
    if success:
        print("\n✅ Migration completed successfully!")
        print("You can now try registering a new user.")
    else:
        print("\n❌ Migration failed. Please check the error above.")
        sys.exit(1)
