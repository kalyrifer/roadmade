"""Create trip_requests table

Revision ID: 001
Revises: 000
Create Date: 2026-04-01 17:59:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '001'
down_revision: Union[str, None] = '000'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Создаем enum тип для статусов заявок (если не существует)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE trip_request_status AS ENUM (
                'pending',
                'confirmed',
                'rejected',
                'cancelled'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Создаем таблицу trip_requests через raw SQL
    op.execute("""
        CREATE TABLE IF NOT EXISTS trip_requests (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
            passenger_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            seats_requested INTEGER NOT NULL,
            message TEXT,
            status trip_request_status NOT NULL DEFAULT 'pending',
            confirmed_at TIMESTAMPTZ,
            rejected_at TIMESTAMPTZ,
            rejected_reason TEXT,
            cancelled_at TIMESTAMPTZ,
            cancelled_by VARCHAR(20),
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            deleted_at TIMESTAMPTZ
        )
    """)
    
    # Создаем индексы
    op.execute("CREATE INDEX IF NOT EXISTS ix_trip_requests_id ON trip_requests (id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_trip_requests_trip_id ON trip_requests (trip_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_trip_requests_passenger_id ON trip_requests (passenger_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_trip_requests_status ON trip_requests (status)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_trip_requests_deleted_at ON trip_requests (deleted_at)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_trip_requests_created_at ON trip_requests (created_at)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS trip_requests CASCADE")
