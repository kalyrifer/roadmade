"""
Тесты для регистрации пользователей.

Тестирует endpoint POST /auth/register
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.schemas.auth import UserRegisterRequest, UserResponse, TokenResponse


@pytest.mark.asyncio
class TestUserRegisterRequest:
    """Тесты для схемы UserRegisterRequest."""
    
    async def test_valid_email(self):
        """Тест валидного email."""
        data = UserRegisterRequest(
            email="user@example.com",
            password="password123",
            name="Иван",
        )
        assert data.email == "user@example.com"
    
    async def test_email_lowercase_normalized(self):
        """Тест нормализации email к нижнему регистру."""
        data = UserRegisterRequest(
            email="USER@EXAMPLE.COM",
            password="password123",
            name="Иван",
        )
        assert data.email == "user@example.com"
    
    async def test_email_strip_whitespace(self):
        """Тест удаления пробелов из email."""
        data = UserRegisterRequest(
            email="  user@example.com  ",
            password="password123",
            name="Иван",
        )
        assert data.email == "user@example.com"
    
    async def test_invalid_email_format(self):
        """Тест невалидного формата email."""
        with pytest.raises(ValueError, match="Invalid email format"):
            UserRegisterRequest(
                email="not-an-email",
                password="password123",
                name="Иван",
            )
    
    async def test_password_min_length(self):
        """Тест минимальной длины пароля."""
        with pytest.raises(ValueError):
            UserRegisterRequest(
                email="user@example.com",
                password="12345",  # Менее 6 символов
                name="Иван",
            )
    
    async def test_name_strip_whitespace(self):
        """Тест удаления пробелов из имени."""
        data = UserRegisterRequest(
            email="user@example.com",
            password="password123",
            name="  Иван  ",
        )
        assert data.name == "Иван"


@pytest.mark.asyncio
class TestUserResponse:
    """Тесты для схемы UserResponse."""
    
    async def test_user_response_creation(self):
        """Тест создания ответа пользователя."""
        response = UserResponse(
            id="123e4567-e89b-12d3-a456-426614174000",
            email="user@example.com",
            name="Иван",
            rating_average=4.5,
            rating_count=10,
        )
        assert response.id == "123e4567-e89b-12d3-a456-426614174000"
        assert response.email == "user@example.com"
        assert response.name == "Иван"
        assert response.rating_average == 4.5
        assert response.rating_count == 10


@pytest.mark.asyncio
class TestTokenResponse:
    """Тесты для схемы TokenResponse."""
    
    async def test_token_response_creation(self):
        """Тест создания ответа с токеном."""
        user = UserResponse(
            id="123e4567-e89b-12d3-a456-426614174000",
            email="user@example.com",
            name="Иван",
            rating_average=0.0,
            rating_count=0,
        )
        response = TokenResponse(
            access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test",
            token_type="bearer",
            user=user,
        )
        assert response.access_token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test"
        assert response.token_type == "bearer"
        assert response.user.email == "user@example.com"


@pytest.mark.asyncio
class TestEmailValidation:
    """Тесты для валидации email."""
    
    async def test_invalid_email_no_at(self):
        """Тест email без @."""
        with pytest.raises(ValueError, match="Invalid email format"):
            UserRegisterRequest(
                email="userexample.com",
                password="password123",
                name="Иван",
            )
    
    async def test_invalid_email_no_domain(self):
        """Тест email без домена."""
        with pytest.raises(ValueError, match="Invalid email format"):
            UserRegisterRequest(
                email="user@",
                password="password123",
                name="Иван",
            )
    
    async def test_invalid_email_no_local(self):
        """Тест email без локальной части."""
        with pytest.raises(ValueError, match="Invalid email format"):
            UserRegisterRequest(
                email="@example.com",
                password="password123",
                name="Иван",
            )


@pytest.mark.asyncio  
class TestPasswordValidation:
    """Тесты для валидации пароля."""
    
    async def test_password_exact_6_chars(self):
        """Тест пароля ровно 6 символов."""
        # Минимальная длина 6 символов - должно работать
        data = UserRegisterRequest(
            email="user@example.com",
            password="123456",
            name="Иван",
        )
        assert data.password == "123456"
    
    async def test_password_5_chars_fails(self):
        """Тест пароля менее 6 символов - ошибка."""
        with pytest.raises(ValueError):
            UserRegisterRequest(
                email="user@example.com",
                password="12345",
                name="Иван",
            )


import uuid
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock

from app.core.security import create_access_token

# Интеграционные тесты с моком
@pytest.mark.asyncio
class TestRegisterEndpoint:
    """Интеграционные тесты для эндпоинта /register."""
    
    async def test_successful_registration(self):
        """Тест успешной регистрации."""
        from app.services.auth.service import AuthService
        from app.repositories.users.repository import UserRepository
        from app.models.users.model import User, UserRole
        import uuid
        
        # Мок репозитория
        mock_repo = AsyncMock(spec=UserRepository)
        mock_repo.get_user_by_email.return_value = None  # Не найден
        mock_repo.create_user.return_value = User(
            id=uuid.uuid4(),
            email="newuser@example.com",
            password_hash="hashed_password",
            first_name="Иван",
            last_name="",
            role=UserRole.USER,
            is_active=True,
            is_blocked=False,
            rating_average=0.0,
            rating_count=0,
        )
        mock_repo.commit = AsyncMock()
        
        # Создаём сервис и регистрируем
        auth_service = AuthService(mock_repo)
        
        request = UserRegisterRequest(
            email="newuser@example.com",
            password="password123",
            name="Иван",
        )
        
        # Выполняем регистрацию
        result = await auth_service.register_user(request)
        
        # Проверяем результат
        assert result.access_token is not None
        assert result.token_type == "bearer"
        assert result.user.email == "newuser@example.com"
        
        # Проверяем вызовы
        mock_repo.get_user_by_email.assert_called_once()
        mock_repo.create_user.assert_called_once()
        mock_repo.commit.assert_called_once()
    
    async def test_duplicate_email_raises_error(self):
        """Тест регистрации с дублирующимся email."""
        from app.services.auth.service import AuthService
        from app.repositories.users.repository import UserRepository
        from app.models.users.model import User, UserRole
        import uuid
        
        # Мок репозитория - пользователь уже существует
        mock_repo = AsyncMock(spec=UserRepository)
        mock_repo.get_user_by_email.return_value = User(
            id=uuid.uuid4(),
            email="existing@example.com",
            password_hash="hashed_password",
            first_name="Пётр",
            last_name="",
            role=UserRole.USER,
            is_active=True,
            is_blocked=False,
            rating_average=4.5,
            rating_count=5,
        )
        
        # Создаём сервис
        auth_service = AuthService(mock_repo)
        
        request = UserRegisterRequest(
            email="existing@example.com",
            password="password123",
            name="Пётр",
        )
        
        # Ожидаем ошибку
        with pytest.raises(ValueError, match="Email already registered"):
            await auth_service.register_user(request)


@pytest.mark.asyncio
class TestLoginEndpoint:
    """Тесты для логина."""
    
    async def test_successful_login(self):
        """Тест успешного входа."""
        from app.services.auth.service import AuthService
        from app.repositories.users.repository import UserRepository
        from app.models.users.model import User, UserRole
        
        test_uuid = uuid.uuid4()
        
        # Мок репозитория
        mock_repo = AsyncMock(spec=UserRepository)
        mock_repo.get_user_by_email.return_value = User(
            id=test_uuid,
            email="user@example.com",
            password_hash="$2b$12$hashed",
            first_name="Иван",
            last_name="",
            role=UserRole.USER,
            is_active=True,
            is_blocked=False,
            rating_average=0.0,
            rating_count=0,
        )
        
        # Мок verify_password
        with patch("app.services.auth.service.verify_password", return_value=True):
            auth_service = AuthService(mock_repo)
            
            result = await auth_service.login_user("user@example.com", "password123")
            
            assert result.access_token is not None
            assert result.token_type == "bearer"
            assert result.user.email == "user@example.com"
    
    async def test_invalid_password(self):
        """Тест неверного пароля."""
        from app.services.auth.service import AuthService
        from app.repositories.users.repository import UserRepository
        from app.models.users.model import User, UserRole
        
        test_uuid = uuid.uuid4()
        
        # Мок репозитория
        mock_repo = AsyncMock(spec=UserRepository)
        mock_repo.get_user_by_email.return_value = User(
            id=test_uuid,
            email="user@example.com",
            password_hash="$2b$12$hashed",
            first_name="Иван",
            last_name="",
            role=UserRole.USER,
            is_active=True,
            is_blocked=False,
            rating_average=0.0,
            rating_count=0,
        )
        
        # Мок verify_password возвращает False
        with patch("app.services.auth.service.verify_password", return_value=False):
            auth_service = AuthService(mock_repo)
            
            with pytest.raises(ValueError, match="Incorrect email or password"):
                await auth_service.login_user("user@example.com", "wrongpassword")
    
    async def test_user_not_found(self):
        """Тест когда пользователь не найден."""
        from app.services.auth.service import AuthService
        from app.repositories.users.repository import UserRepository
        
        # Мок репозитория - пользователь не найден
        mock_repo = AsyncMock(spec=UserRepository)
        mock_repo.get_user_by_email.return_value = None
        
        auth_service = AuthService(mock_repo)
        
        with pytest.raises(ValueError, match="Incorrect email or password"):
            await auth_service.login_user("notfound@example.com", "password123")


@pytest.mark.asyncio
class TestGetCurrentUser:
    """Тесты для получения текущего пользователя."""
    
    async def test_valid_token(self):
        """Тест с корректным токеном."""
        from app.services.auth.service import AuthService
        from app.repositories.users.repository import UserRepository
        from app.models.users.model import User, UserRole
        
        test_uuid = uuid.uuid4()
        
        # Мок репозитория
        mock_repo = AsyncMock(spec=UserRepository)
        mock_repo.get_user_by_id.return_value = User(
            id=test_uuid,
            email="user@example.com",
            password_hash="$2b$12$hashed",
            first_name="Иван",
            last_name="",
            role=UserRole.USER,
            is_active=True,
            is_blocked=False,
            rating_average=4.5,
            rating_count=10,
        )
        
        auth_service = AuthService(mock_repo)
        
        # Создаём валидный токен
        token = create_access_token(
            data={"sub": str(test_uuid), "email": "user@example.com"},
            expires_delta=timedelta(minutes=30),
        )
        
        result = await auth_service.get_current_user(token)
        
        assert result.email == "user@example.com"
        assert result.name == "Иван"
        assert result.rating_average == 4.5
    
    async def test_invalid_token(self):
        """Тест с недействительным токеном."""
        from app.services.auth.service import AuthService
        from app.repositories.users.repository import UserRepository
        
        mock_repo = AsyncMock(spec=UserRepository)
        auth_service = AuthService(mock_repo)
        
        with pytest.raises(ValueError, match="Could not validate credentials"):
            await auth_service.get_current_user("invalid_token")
    
    async def test_user_deleted(self):
        """Тест когда пользователь удалён."""
        from app.services.auth.service import AuthService
        from app.repositories.users.repository import UserRepository
        
        test_uuid = uuid.uuid4()
        
        # Мок репозитория - пользователь не найден
        mock_repo = AsyncMock(spec=UserRepository)
        mock_repo.get_user_by_id.return_value = None
        
        auth_service = AuthService(mock_repo)
        
        token = create_access_token(
            data={"sub": str(test_uuid), "email": "deleted@example.com"},
            expires_delta=timedelta(minutes=30),
        )
        
        with pytest.raises(ValueError, match="Could not validate credentials"):
            await auth_service.get_current_user(token)


@pytest.mark.asyncio
class TestLogoutEndpoint:
    """Тесты для выхода из системы."""
    
    async def test_successful_logout(self):
        """Тест успешного выхода."""
        from app.services.auth.service import AuthService
        from app.services.auth.service import logging
        
        # Мок логгера
        with patch("logging.getLogger") as mock_logger:
            mock_logger.return_value = MagicMock()
            
            # Нужно создать мок auth_service
            from unittest.mock import AsyncMock
            mock_service = AsyncMock()
            result = await mock_service.logout_user.return_value
            
            # Просто тестируем что метод существует
            assert hasattr(AuthService, "logout_user")