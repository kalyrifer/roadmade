"""Create missing PostgreSQL enum types

Revision ID: 009_create_enum_types
Revises: 008_fix_enum_types
Create Date: 2026-04-03 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = '009_create_enum_types'
down_revision: Union[str, None] = '008_fix_enum_types'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Создаём отсутствующие PostgreSQL enum типы.
    Проблема: предыдущие миграции могли не создать типы из-за ошибок.
    """
    
    # Создаём user_role если не существует
    op.execute("""
        DO $$
        BEGIN
            CREATE TYPE "user_role" AS ENUM ('user', 'admin');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Создаём trip_status если не существует
    op.execute("""
        DO $$
        BEGIN
            CREATE TYPE "trip_status" AS ENUM ('draft', 'published', 'active', 'completed', 'cancelled');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Создаём trip_request_status если не существует
    op.execute("""
        DO $$
        BEGIN
            CREATE TYPE "trip_request_status" AS ENUM ('pending', 'confirmed', 'rejected', 'cancelled');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Создаём review_status если не существует
    op.execute("""
        DO $$
        BEGIN
            CREATE TYPE "review_status" AS ENUM ('pending', 'published', 'rejected');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Создаём notification_type если не существует (критичный!)
    op.execute("""
        DO $$
        BEGIN
            CREATE TYPE "notification_type" AS ENUM (
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
    
    # Создаём conversation_status если не существует
    op.execute("""
        DO $$
        BEGIN
            CREATE TYPE "conversation_status" AS ENUM ('active', 'archived');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)


def downgrade() -> None:
    """Откат не требуется - enum типы удалять опасно."""
    pass