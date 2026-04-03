"""
Конфигурация pytest для тестов.

Содержит фикстуры для:
- AsyncSession мок
- Тестовый клиент
"""
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock


@pytest.fixture
def anyio_backend():
    """Фикстура для anyio."""
    return "asyncio"


@pytest_asyncio.fixture
async def mock_db_session():
    """Фикстура для мока сессии БД."""
    session = AsyncMock()
    session.add = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    return session


@pytest.fixture
def sample_user_data():
    """Фикстура с тестовыми данными пользователя."""
    return {
        "email": "test@example.com",
        "password": "password123",
        "name": "Тест",
    }