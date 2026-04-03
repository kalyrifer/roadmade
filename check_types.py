"""
Check existing enum types in the database.
Run with: python -c "$(cat check_types.py)"
"""
import asyncio
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/roadmate_db"

def check_types():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT typname FROM pg_type WHERE typname LIKE '%status%'"))
        types = [row[0] for row in result]
        print("Existing types containing 'status':")
        for t in types:
            print(f"  - {t}")
        
        if not types:
            print("No types found!")
        
        # Check all enum types
        result2 = conn.execute(text("SELECT typname FROM pg_type WHERE typtype = 'e'"))
        enum_types = [row[0] for row in result2]
        print("\nAll enum types:")
        for t in enum_types:
            print(f"  - {t}")

if __name__ == "__main__":
    check_types()