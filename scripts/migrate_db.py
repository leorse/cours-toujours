import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from sqlmodel import SQLModel, text
from src.database import engine
from src.models import ExerciseLog

def migrate():
    print("Migrating database...")
    with engine.connect() as conn:
        # Add session_config column to course if not exists
        # SQLite doesn't support IF NOT EXISTS for columns easily, so we try/except
        try:
            conn.execute(text("ALTER TABLE course ADD COLUMN session_config JSON"))
            print("Added session_config column to course table.")
        except Exception as e:
            print(f"Column might already exist or error: {e}")

    # Create new tables
    SQLModel.metadata.create_all(engine)
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
