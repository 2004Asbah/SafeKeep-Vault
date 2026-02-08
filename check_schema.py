import sqlite3
import sys
import os

# Path to the database
db_path = os.path.join(os.getcwd(), 'backend', 'safekeep.db')

def check_schema():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get the schema for the users table
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    
    print("Current users table schema:")
    print(f"{'CID':<5} {'Name':<20} {'Type':<15} {'NotNull':<10} {'Default':<15}")
    print("-" * 70)
    for col in columns:
        cid, name, type_, notnull, default, pk = col
        print(f"{cid:<5} {name:<20} {type_:<15} {notnull:<10} {str(default):<15}")
    
    # Check if 'role' column exists
    column_names = [col[1] for col in columns]
    if 'role' not in column_names:
        print("\n⚠️ WARNING: 'role' column is MISSING from users table!")
        print("This is likely causing the 500 error during registration.")
    else:
        print("\n✓ 'role' column exists in users table")
    
    conn.close()

if __name__ == "__main__":
    check_schema()
