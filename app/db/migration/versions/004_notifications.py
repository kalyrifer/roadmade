"""
Add notifications table

Revision ID: 004_notifications
Revises: 003_reviews
Create Date: 2025-04-01 18:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '004_notifications'
down_revision: Union[str, None] = '003_reviews'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create notifications table."""
    # Create enum type for notification type if not exists
    op.execute("""
        DO $$ BEGIN
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
    
    # === notifications ===
    op.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            type notification_type NOT NULL,
            title VARCHAR(255) NOT NULL,
            message TEXT NOT NULL,
            is_read BOOLEAN NOT NULL DEFAULT false,
            related_trip_id UUID REFERENCES trips(id) ON DELETE SET NULL,
            related_request_id UUID REFERENCES trip_requests(id) ON DELETE SET NULL,
            read_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    
    # Create indexes
    op.execute("CREATE INDEX IF NOT EXISTS ix_notifications_user_id ON notifications (user_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_notifications_is_read ON notifications (is_read)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_notifications_created_at ON notifications (created_at)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_notifications_type ON notifications (type)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_notifications_related_trip_id ON notifications (related_trip_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_notifications_related_request_id ON notifications (related_request_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_notifications_user_unread ON notifications (user_id, is_read)")


def downgrade() -> None:
    """Drop notifications table."""
    op.execute("DROP TABLE IF EXISTS notifications CASCADE")
