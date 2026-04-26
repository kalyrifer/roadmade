"""
Recalculate aggregated user rating columns from published reviews

Revision ID: 012_recalc_user_ratings
Revises: 011_publish_pending_reviews
Create Date: 2026-04-26 17:30:00.000000
"""
from typing import Sequence, Union

from alembic import op


revision: str = '012_recalc_user_ratings'
down_revision: Union[str, None] = '011_publish_pending_reviews'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Recompute users.rating_average and users.rating_count from published reviews."""
    op.execute("""
        UPDATE users u
        SET rating_average = COALESCE(agg.avg_rating, 0.00),
            rating_count = COALESCE(agg.cnt, 0),
            updated_at = now()
        FROM (
            SELECT target_id,
                   ROUND(AVG(rating)::numeric, 2) AS avg_rating,
                   COUNT(*) AS cnt
            FROM reviews
            WHERE status = 'published'
            GROUP BY target_id
        ) agg
        WHERE u.id = agg.target_id
    """)


def downgrade() -> None:
    """No-op: aggregated rating recomputation is not reversible."""
    pass
