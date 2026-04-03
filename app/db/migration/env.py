# Alembic env.py file for RoadMate
import os
from logging.config import fileConfig

from sqlalchemy import create_engine, pool

from alembic import context

# Import config from alembic.ini
config = context.config

# Get database URL from env - convert async to sync
DATABASE_URL = os.getenv("DATABASE_URL_SYNC", os.getenv("DATABASE_URL", ""))
if DATABASE_URL and "postgresql+asyncpg" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg", "postgresql")
elif DATABASE_URL and "postgresql+psycopg2" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql+psycopg2", "postgresql")
if not DATABASE_URL:
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/roadmate2"

config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import all models explicitly to register them with Base
from app.db.base import Base
from app.models.users.model import User, UserRole  # noqa: F401
from app.models.users.settings import UserSettings  # noqa: F401
from app.models.trips.model import Trip  # noqa: F401
from app.models.requests.model import TripRequest  # noqa: F401
from app.models.chat.model import Conversation, Message, ConversationParticipant  # noqa: F401
from app.models.reviews.model import Review  # noqa: F401
from app.models.notifications.model import Notification, NotificationType  # noqa: F401

# Set target metadata for autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = create_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()