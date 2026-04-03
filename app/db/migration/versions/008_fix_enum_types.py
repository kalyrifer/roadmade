"""Fix missing enum types in database

Revision ID: 008_fix_enum_types
Revises: 007_add_related_conversation
Create Date: 2026-04-03 10:40:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = '008_fix_enum_types'
down_revision: Union[str, None] = '007_add_related_conversation'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Создаём enum типы, которые могут отсутствовать в базе данных.
    Проблема: при использовании CREATE TYPE ... IF NOT EXISTS PostgreSQL
    выбрасывает ошибку, а не пропускает создание.
    """
    
    # Создаём user_role если не существует
    op.execute("""
        DO $$
        BEGIN
            CREATE TYPE user_role AS ENUM ('user', 'admin');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Создаём trip_status если не существует
    op.execute("""
        DO $$
        BEGIN
            CREATE TYPE trip_status AS ENUM ('draft', 'published', 'active', 'completed', 'cancelled');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Создаём trip_request_status если не существует
    op.execute("""
        DO $$
        BEGIN
            CREATE TYPE trip_request_status AS ENUM ('pending', 'confirmed', 'rejected', 'cancelled');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Создаём review_status если не существует
    op.execute("""
        DO $$
        BEGIN
            CREATE TYPE review_status AS ENUM ('pending', 'published', 'rejected');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Создаём notification_type если не существует
    op.execute("""
        DO $$
        BEGIN
            CREATE TYPE notification_type AS ENUM (
                'request_new',
                'request_confirmed',
                'request_rejected',
                'request_cancelled',
                'trip_cancelled',
                'trip_completed',
                'message_new',
                'system'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)


def downgrade() -> None:
    """Откат не требуется - enum типы удалять опасно."""
    pass