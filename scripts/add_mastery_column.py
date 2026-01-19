import sqlite3
import os

DB_PATH = "content.db"

def migrate():
    print(f"Migrating database at {DB_PATH}...")
    
    if not os.path.exists(DB_PATH):
        print("Database not found!")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(roadstepprogress)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if "mastery" not in columns:
            print("Adding 'mastery' column to RoadStepProgress...")
            cursor.execute("ALTER TABLE roadstepprogress ADD COLUMN mastery INTEGER DEFAULT 0")
            conn.commit()
            print("Migration successful.")
        else:
            print("Column 'mastery' already exists.")
            
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
