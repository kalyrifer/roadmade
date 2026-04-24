import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    user="postgres",
    password="postgres",
    database="roadmate_db"
)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cursor = conn.cursor()

# Create enum type
try:
    cursor.execute('CREATE TYPE userrole AS ENUM (%s, %s)', ('user', 'admin'))
    print('Created enum userrole')
except Exception as e:
    print(f'Enum error: {e}')

# Create users table
try:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
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
            role VARCHAR(20) NOT NULL DEFAULT 'user',
            is_active BOOLEAN NOT NULL DEFAULT true,
            is_blocked BOOLEAN NOT NULL DEFAULT false,
            language VARCHAR(10) NOT NULL DEFAULT 'ru',
            timezone VARCHAR(50) NOT NULL DEFAULT 'Europe/Moscow',
            last_login_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    ''')
    print('Created table users')
except Exception as e:
    print(f'Users table error: {e}')

# Create alembic_version table
try:
    cursor.execute('CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32))')
    print('Created alembic_version')
except Exception as e:
    print(f'Alembic table error: {e}')

cursor.close()
conn.close()
print('Migration done!')