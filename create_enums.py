"""
Create missing enum types in the database directly.
"""
import asyncio
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/roadmate_db"

def create_enum_types():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        # Создаём тип trip_request_status если не существует
        try:
            conn.execute(text("""
                DO $$
                BEGIN
                    CREATE TYPE trip_request_status AS ENUM ('pending', 'confirmed', 'rejected', 'cancelled');
                EXCEPTION
                    WHEN duplicate_object THEN null;
                END $$;
            """))
            print("Created trip_request_status enum type")
        except Exception as e:
            print(f"Error creating trip_request_status: {e}")
        
        # Создаём остальные типы
        types = [
            ("user_role", "('user', 'admin')"),
            ("trip_status", "('draft', 'published', 'active', 'completed', 'cancelled')"),
            ("review_status", "('pending', 'published', 'rejected')"),
            ("notification_type", "('request_new', 'request_confirmed', 'request_rejected', 'request_cancelled', 'trip_cancelled', 'trip_completed', 'message_new', 'system')"),
        ]
        
        for type_name, values in types:
            try:
                conn.execute(text(f"""
                    DO $$
                    BEGIN
                        CREATE TYPE {type_name} AS ENUM {values};
                    EXCEPTION
                        WHEN duplicate_object THEN null;
                    END $$;
                """))
                print(f"Created {type_name} enum type")
            except Exception as e:
                print(f"Error creating {type_name}: {e}")
        
        conn.commit()
        
        # Проверяем что получилось
        result = conn.execute(text("SELECT typname FROM pg_type WHERE typtype = 'e'"))
        enum_types = [row[0] for row in result]
        print(f"\nAll enum types in database: {enum_types}")

if __name__ == "__main__":
    create_enum_types()