"""
Add chat tables (conversations, conversation_participants, messages)

Revision ID: 002_chat
Revises: 001
Create Date: 2025-04-01 12:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '002_chat'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create chat tables using raw SQL to avoid FK ordering issues."""
    # === conversations ===
    op.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            last_message_at TIMESTAMPTZ
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_conversations_trip_id ON conversations (trip_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_conversations_last_message_at ON conversations (last_message_at)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_conversations_created_at ON conversations (created_at)")

    # === messages (создаём перед conversation_participants, т.к. есть FK на messages) ===
    op.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
            sender_id UUID REFERENCES users(id) ON DELETE SET NULL,
            content TEXT NOT NULL,
            is_read BOOLEAN NOT NULL DEFAULT false,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_messages_conversation_id ON messages (conversation_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_messages_sender_id ON messages (sender_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_messages_created_at ON messages (created_at)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_messages_is_read ON messages (is_read)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_messages_conversation_created ON messages (conversation_id, created_at)")

    # === conversation_participants (теперь можно ссылаться на messages) ===
    op.execute("""
        CREATE TABLE IF NOT EXISTS conversation_participants (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            is_muted BOOLEAN NOT NULL DEFAULT false,
            last_read_message_id UUID REFERENCES messages(id) ON DELETE SET NULL,
            joined_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_conversation_participants_conversation_id ON conversation_participants (conversation_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_conversation_participants_user_id ON conversation_participants (user_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_conversation_participants_joined_at ON conversation_participants (joined_at)")
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_conversation_participants_unique ON conversation_participants (conversation_id, user_id)")


def downgrade() -> None:
    """Drop chat tables."""
    op.execute("DROP TABLE IF EXISTS conversation_participants CASCADE")
    op.execute("DROP TABLE IF EXISTS messages CASCADE")
    op.execute("DROP TABLE IF EXISTS conversations CASCADE")
