#!/usr/bin/env python3
"""
SandWACH Database Setup
Initialize SQLite database with required tables
"""

import sqlite3
import os
from config import DATABASE_FILE

def setup_database():
    """Create database tables and initial data"""
    print("Setting up SandWACH database...")

    # Create database directory if it doesn't exist
    db_dir = os.path.dirname(DATABASE_FILE)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)

    # Connect to database
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    try:
        # Create weather_cache table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_cache (
                timestamp INTEGER PRIMARY KEY,
                data TEXT NOT NULL
            )
        ''')

        # Create notifications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL CHECK (type IN ('evening', 'morning')),
                content TEXT NOT NULL,
                sent_at INTEGER NOT NULL
            )
        ''')

        # Create indexes for performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_notifications_sent_at
            ON notifications(sent_at)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_notifications_type
            ON notifications(type)
        ''')

        # Commit changes
        conn.commit()

        print(f"Database setup complete: {DATABASE_FILE}")
        print("Tables created:")
        print("  - weather_cache")
        print("  - notifications")

        # Show table info
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"\nCreated tables: {[table[0] for table in tables]}")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
    finally:
        conn.close()

def show_database_info():
    """Show information about the database"""
    if not os.path.exists(DATABASE_FILE):
        print(f"Database file does not exist: {DATABASE_FILE}")
        return

    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    try:
        # Show tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables: {[table[0] for table in tables]}")

        # Show notifications count
        cursor.execute("SELECT COUNT(*) FROM notifications")
        count = cursor.fetchone()[0]
        print(f"Total notifications: {count}")

        # Show recent notifications
        cursor.execute("""
            SELECT type, sent_at, substr(content, 1, 50) || '...'
            FROM notifications
            ORDER BY sent_at DESC
            LIMIT 3
        """)
        recent = cursor.fetchall()
        if recent:
            print("Recent notifications:")
            for notif in recent:
                print(f"  {notif[0]}: {notif[2]}")

    except sqlite3.Error as e:
        print(f"Error reading database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "info":
        show_database_info()
    else:
        setup_database()
