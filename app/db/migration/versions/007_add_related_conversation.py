"""Add related_conversation_id to notifications

Revision ID: 007_add_related_conversation
Revises: 006_rebuild_core_schema
Create Date: 2026-04-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '007_add_related_conversation'
down_revision: Union[str, None] = '006_rebuild_core_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add the related_conversation_id column
    op.add_column(
        'notifications',
        sa.Column(
            'related_conversation_id',
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                'conversations.id',
                ondelete='SET NULL'
            ),
            nullable=True,
            index=True
        )
    )


def downgrade() -> None:
    op.drop_column('notifications', 'related_conversation_id')