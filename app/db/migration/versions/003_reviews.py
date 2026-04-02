"""
Add reviews table

Revision ID: 003_reviews
Revises: 002_chat
Create Date: 2025-04-01 15:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '003_reviews'
down_revision: Union[str, None] = '002_chat'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create reviews table."""
    # Create enum type for review status if not exists
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE review_status AS ENUM ('pending', 'published', 'rejected');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # === reviews ===
    op.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
            author_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            target_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            rating SMALLINT NOT NULL,
            text TEXT,
            status review_status NOT NULL DEFAULT 'pending',
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT uq_reviews_trip_author UNIQUE (trip_id, author_id)
        )
    """)
    
    # Create indexes
    op.execute("CREATE INDEX IF NOT EXISTS ix_reviews_trip_id ON reviews (trip_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_reviews_author_id ON reviews (author_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_reviews_target_id ON reviews (target_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_reviews_status ON reviews (status)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_reviews_created_at ON reviews (created_at)")


def downgrade() -> None:
    """Drop reviews table."""
    op.execute("DROP TABLE IF EXISTS reviews CASCADE")
