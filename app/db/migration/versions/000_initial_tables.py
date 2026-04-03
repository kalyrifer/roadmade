"""Create initial tables: users, user_settings, trips

Revision ID: 000
Revises: 
Create Date: 2026-04-02 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '000'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Создаем enum типы (если не существуют)
    # SQLAlchemy по умолчанию создаёт имя enum из имени класса: UserRole -> userrole
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE "userrole" AS ENUM ('user', 'admin');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE trip_status AS ENUM ('draft', 'published', 'active', 'completed', 'cancelled');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE tripstatus AS ENUM ('draft', 'published', 'active', 'completed', 'cancelled');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Создаем таблицу users
    op.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email VARCHAR(255) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            phone VARCHAR(20),
            avatar_url VARCHAR(500),
            bio TEXT,
            rating_average NUMERIC(3, 2) NOT NULL DEFAULT 0.00,
            rating_count INTEGER NOT NULL DEFAULT 0,
            role "userrole" NOT NULL DEFAULT 'user',
            is_active BOOLEAN NOT NULL DEFAULT true,
            is_blocked BOOLEAN NOT NULL DEFAULT false,
            is_email_verified BOOLEAN NOT NULL DEFAULT false,
            is_phone_verified BOOLEAN NOT NULL DEFAULT false,
            is_two_factor_enabled BOOLEAN NOT NULL DEFAULT false,
            language VARCHAR(10) NOT NULL DEFAULT 'ru',
            timezone VARCHAR(50) NOT NULL DEFAULT 'Europe/Moscow',
            last_login_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            deleted_at TIMESTAMPTZ
        )
    """)
    
    # Индексы для users
    op.execute("CREATE INDEX IF NOT EXISTS ix_users_email ON users (email)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_users_phone ON users (phone)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_users_role ON users (role)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_users_is_active ON users (is_active)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_users_is_blocked ON users (is_blocked)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_users_deleted_at ON users (deleted_at)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_users_rating_average ON users (rating_average)")
    
    # Создаем таблицу user_settings
    op.execute("""
        CREATE TABLE IF NOT EXISTS user_settings (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
            notifications_enabled BOOLEAN NOT NULL DEFAULT true,
            email_notifications BOOLEAN NOT NULL DEFAULT true,
            push_notifications BOOLEAN NOT NULL DEFAULT false,
            show_profile_publicly BOOLEAN NOT NULL DEFAULT true,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    
    # Создаем таблицу trips
    op.execute("""
        CREATE TABLE IF NOT EXISTS trips (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            driver_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            from_address VARCHAR(500) NOT NULL,
            from_lat DOUBLE PRECISION,
            from_lng DOUBLE PRECISION,
            to_address VARCHAR(500) NOT NULL,
            to_lat DOUBLE PRECISION,
            to_lng DOUBLE PRECISION,
            departure_time TIMESTAMPTZ NOT NULL,
            arrival_time TIMESTAMPTZ,
            available_seats INTEGER NOT NULL,
            price NUMERIC(10, 2) NOT NULL,
            status trip_status NOT NULL DEFAULT 'draft',
            description TEXT,
            params JSON,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            deleted_at TIMESTAMPTZ
        )
    """)
    
    # Индексы для trips
    op.execute("CREATE INDEX IF NOT EXISTS ix_trips_id ON trips (id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_trips_driver_id ON trips (driver_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_trips_status ON trips (status)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_trips_departure_time ON trips (departure_time)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_trips_deleted_at ON trips (deleted_at)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_trips_from_address ON trips (from_address)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_trips_to_address ON trips (to_address)")


def downgrade() -> None:
    # Удаляем trips
    op.execute("DROP TABLE IF EXISTS trips CASCADE")
    
    # Удаляем user_settings
    op.execute("DROP TABLE IF EXISTS user_settings CASCADE")
    
    # Удаляем users
    op.execute("DROP TABLE IF EXISTS users CASCADE")
