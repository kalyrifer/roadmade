import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def check():
    engine = create_async_engine('postgresql+asyncpg://postgres:postgres@localhost:5432/roadmate_db')
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT id, email, first_name, is_active, is_blocked, LENGTH(password_hash) as pw_len FROM users"))
        rows = result.fetchall()
        for row in rows:
            print(f'User: {row}')
    await engine.dispose()

asyncio.run(check())