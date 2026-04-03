"""Fix legacy tripstatus enum name for ORM compatibility

Revision ID: 005_fix_tripstatus_enum
Revises: 004_notifications
Create Date: 2026-04-02 19:18:00.000000
"""

from typing import Sequence, Union

from alembic import op


revision: str = '005_fix_tripstatus_enum'
down_revision: Union[str, None] = '004_notifications'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            CREATE TYPE tripstatus AS ENUM ('draft', 'published', 'active', 'completed', 'cancelled');
        EXCEPTION
            WHEN duplicate_object THEN NULL;
        END $$;
        """
    )


def downgrade() -> None:
    op.execute("DROP TYPE IF EXISTS tripstatus")
