"""Rebuild core schema to match current ORM models

Revision ID: 006_rebuild_core_schema
Revises: 005_fix_tripstatus_enum
Create Date: 2026-04-02 19:22:00.000000
"""

from typing import Sequence, Union

from alembic import op


revision: str = '006_rebuild_core_schema'
down_revision: Union[str, None] = '005_fix_tripstatus_enum'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DROP TABLE IF EXISTS notifications CASCADE")
    op.execute("DROP TABLE IF EXISTS reviews CASCADE")
    op.execute("DROP TABLE IF EXISTS conversation_participants CASCADE")
    op.execute("DROP TABLE IF EXISTS messages CASCADE")
    op.execute("DROP TABLE IF EXISTS conversations CASCADE")
    op.execute("DROP TABLE IF EXISTS trip_requests CASCADE")
    op.execute("DROP TABLE IF EXISTS trips CASCADE")
    op.execute("DROP TABLE IF EXISTS user_settings CASCADE")
    op.execute("DROP TABLE IF EXISTS users CASCADE")

    op.execute("DROP TYPE IF EXISTS notification_type CASCADE")
    op.execute("DROP TYPE IF EXISTS review_status CASCADE")
    op.execute("DROP TYPE IF EXISTS trip_request_status CASCADE")
    op.execute("DROP TYPE IF EXISTS tripstatus CASCADE")
    op.execute("DROP TYPE IF EXISTS trip_status CASCADE")
    op.execute("DROP TYPE IF EXISTS user_role CASCADE")
    op.execute("DROP TYPE IF EXISTS userrole CASCADE")

    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE user_role AS ENUM ('user', 'admin');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
        """
    )
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE trip_status AS ENUM ('draft', 'published', 'active', 'completed', 'cancelled');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
        """
    )
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE trip_request_status AS ENUM ('pending', 'confirmed', 'rejected', 'cancelled');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
        """
    )
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE review_status AS ENUM ('pending', 'published', 'rejected');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
        """
    )
    op.execute(
        """
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
        """
    )

    op.execute(
        """
        CREATE TABLE users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email VARCHAR(255) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL DEFAULT '',
            phone VARCHAR(20),
            avatar_url VARCHAR(500),
            bio TEXT,
            rating_average NUMERIC(3, 2) NOT NULL DEFAULT 0.00,
            rating_count INTEGER NOT NULL DEFAULT 0,
            role user_role NOT NULL DEFAULT 'user',
            is_active BOOLEAN NOT NULL DEFAULT true,
            is_blocked BOOLEAN NOT NULL DEFAULT false,
            is_email_verified BOOLEAN NOT NULL DEFAULT false,
            is_phone_verified BOOLEAN NOT NULL DEFAULT false,
            is_two_factor_enabled BOOLEAN NOT NULL DEFAULT false,
            language VARCHAR(10) NOT NULL DEFAULT 'ru',
            timezone VARCHAR(50) NOT NULL DEFAULT 'Europe/Moscow',
            last_login_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            deleted_at TIMESTAMPTZ
        )
        """
    )

    op.execute(
        """
        CREATE TABLE user_settings (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
            notifications_enabled BOOLEAN NOT NULL DEFAULT true,
            email_notifications BOOLEAN NOT NULL DEFAULT true,
            push_notifications BOOLEAN NOT NULL DEFAULT false,
            show_profile_publicly BOOLEAN NOT NULL DEFAULT true,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE trips (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            driver_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            from_city VARCHAR(100) NOT NULL,
            from_address VARCHAR(255),
            to_city VARCHAR(100) NOT NULL,
            to_address VARCHAR(255),
            departure_date DATE NOT NULL,
            departure_time_start TIME NOT NULL,
            departure_time_end TIME,
            is_time_range BOOLEAN NOT NULL DEFAULT false,
            arrival_time TIME,
            price_per_seat NUMERIC(10, 2) NOT NULL,
            total_seats INTEGER NOT NULL,
            available_seats INTEGER NOT NULL,
            description TEXT,
            luggage_allowed BOOLEAN NOT NULL DEFAULT true,
            smoking_allowed BOOLEAN NOT NULL DEFAULT false,
            music_allowed BOOLEAN NOT NULL DEFAULT true,
            pets_allowed BOOLEAN NOT NULL DEFAULT false,
            car_model VARCHAR(100),
            car_color VARCHAR(50),
            car_license_plate VARCHAR(20),
            status trip_status NOT NULL DEFAULT 'draft',
            cancelled_at TIMESTAMPTZ,
            cancelled_reason TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            deleted_at TIMESTAMPTZ
        )
        """
    )

    op.execute(
        """
        CREATE TABLE trip_requests (
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
        """
    )

    op.execute(
        """
        CREATE TABLE conversations (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            last_message_at TIMESTAMPTZ
        )
        """
    )

    op.execute(
        """
        CREATE TABLE messages (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
            sender_id UUID REFERENCES users(id) ON DELETE SET NULL,
            content TEXT NOT NULL,
            is_read BOOLEAN NOT NULL DEFAULT false,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE conversation_participants (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            is_muted BOOLEAN NOT NULL DEFAULT false,
            last_read_message_id UUID REFERENCES messages(id) ON DELETE SET NULL,
            joined_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE reviews (
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
        """
    )

    op.execute(
        """
        CREATE TABLE notifications (
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
        """
    )

    op.execute("CREATE INDEX ix_users_email ON users (email)")
    op.execute("CREATE INDEX ix_users_phone ON users (phone)")
    op.execute("CREATE INDEX ix_users_role ON users (role)")
    op.execute("CREATE INDEX ix_users_is_active ON users (is_active)")
    op.execute("CREATE INDEX ix_users_is_blocked ON users (is_blocked)")
    op.execute("CREATE INDEX ix_users_deleted_at ON users (deleted_at)")
    op.execute("CREATE INDEX ix_users_rating_average ON users (rating_average)")

    op.execute("CREATE INDEX ix_trips_driver_id ON trips (driver_id)")
    op.execute("CREATE INDEX ix_trips_from_city ON trips (from_city)")
    op.execute("CREATE INDEX ix_trips_to_city ON trips (to_city)")
    op.execute("CREATE INDEX ix_trips_departure_date ON trips (departure_date)")
    op.execute("CREATE INDEX ix_trips_price_per_seat ON trips (price_per_seat)")
    op.execute("CREATE INDEX ix_trips_available_seats ON trips (available_seats)")
    op.execute("CREATE INDEX ix_trips_status ON trips (status)")
    op.execute("CREATE INDEX ix_trips_deleted_at ON trips (deleted_at)")

    op.execute("CREATE INDEX ix_trip_requests_trip_id ON trip_requests (trip_id)")
    op.execute("CREATE INDEX ix_trip_requests_passenger_id ON trip_requests (passenger_id)")
    op.execute("CREATE INDEX ix_trip_requests_status ON trip_requests (status)")
    op.execute("CREATE INDEX ix_trip_requests_deleted_at ON trip_requests (deleted_at)")
    op.execute("CREATE INDEX ix_trip_requests_created_at ON trip_requests (created_at)")

    op.execute("CREATE INDEX ix_conversations_trip_id ON conversations (trip_id)")
    op.execute("CREATE INDEX ix_conversations_last_message_at ON conversations (last_message_at)")
    op.execute("CREATE INDEX ix_conversations_created_at ON conversations (created_at)")

    op.execute("CREATE INDEX ix_messages_conversation_id ON messages (conversation_id)")
    op.execute("CREATE INDEX ix_messages_sender_id ON messages (sender_id)")
    op.execute("CREATE INDEX ix_messages_created_at ON messages (created_at)")
    op.execute("CREATE INDEX ix_messages_is_read ON messages (is_read)")

    op.execute("CREATE INDEX ix_conversation_participants_conversation_id ON conversation_participants (conversation_id)")
    op.execute("CREATE INDEX ix_conversation_participants_user_id ON conversation_participants (user_id)")
    op.execute("CREATE UNIQUE INDEX ix_conversation_participants_unique ON conversation_participants (conversation_id, user_id)")

    op.execute("CREATE INDEX ix_reviews_trip_id ON reviews (trip_id)")
    op.execute("CREATE INDEX ix_reviews_author_id ON reviews (author_id)")
    op.execute("CREATE INDEX ix_reviews_target_id ON reviews (target_id)")
    op.execute("CREATE INDEX ix_reviews_status ON reviews (status)")
    op.execute("CREATE INDEX ix_reviews_created_at ON reviews (created_at)")

    op.execute("CREATE INDEX ix_notifications_user_id ON notifications (user_id)")
    op.execute("CREATE INDEX ix_notifications_is_read ON notifications (is_read)")
    op.execute("CREATE INDEX ix_notifications_created_at ON notifications (created_at)")
    op.execute("CREATE INDEX ix_notifications_type ON notifications (type)")
    op.execute("CREATE INDEX ix_notifications_related_trip_id ON notifications (related_trip_id)")
    op.execute("CREATE INDEX ix_notifications_related_request_id ON notifications (related_request_id)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS notifications CASCADE")
    op.execute("DROP TABLE IF EXISTS reviews CASCADE")
    op.execute("DROP TABLE IF EXISTS conversation_participants CASCADE")
    op.execute("DROP TABLE IF EXISTS messages CASCADE")
    op.execute("DROP TABLE IF EXISTS conversations CASCADE")
    op.execute("DROP TABLE IF EXISTS trip_requests CASCADE")
    op.execute("DROP TABLE IF EXISTS trips CASCADE")
    op.execute("DROP TABLE IF EXISTS user_settings CASCADE")
    op.execute("DROP TABLE IF EXISTS users CASCADE")
    op.execute("DROP TYPE IF EXISTS notification_type CASCADE")
    op.execute("DROP TYPE IF EXISTS review_status CASCADE")
    op.execute("DROP TYPE IF EXISTS trip_request_status CASCADE")
    op.execute("DROP TYPE IF EXISTS trip_status CASCADE")
    op.execute("DROP TYPE IF EXISTS user_role CASCADE")
