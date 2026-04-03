"""
Тесты для просмотра и редактирования профиля пользователя.

Тесты включают:
- Просмотр своего профиля
- Просмотр чужого профиля (без прав) -> 403
- Админ может любой профиль
- Успешное обновление данных
- Смена аватара
- Попытка редактирования чужого профиля -> 403
- Неверный формат аватара -> 400
"""
import pytest
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import HTTPException

from app.models.users.model import User, UserRole
from app.schemas.users.schemas import UserUpdateRequest
from app.services.users.service import UserService


# Тестовые данные

def create_test_user(
    user_id: str = "550e8400-e29b-41d4-a716-446655440000",
    email: str = "test@example.com",
    first_name: str = "Иван",
    last_name: str = "Петров",
    role: UserRole = UserRole.USER,
    is_active: bool = True,
    is_blocked: bool = False,
) -> User:
    """
    Создание тестового пользователя.
    
    Args:
        user_id: UUID пользователя
        email: Email
        first_name: Имя
        last_name: Фамилия
        role: Роль
        is_active: Активен
        is_blocked: Заблокирован
        
    Returns:
        User: Тестовый пользователь
    """
    user = MagicMock(spec=User)
    user.id = uuid.UUID(user_id)
    user.email = email
    user.first_name = first_name
    user.last_name = last_name
    user.phone = "+79001234567"
    user.avatar_url = None
    user.bio = "Тестовое описание"
    user.rating_average = 4.5
    user.rating_count = 10
    user.role = role
    user.is_active = is_active
    user.is_blocked = is_blocked
    user.created_at = datetime.utcnow()
    return user


class TestUserSchemas:
    """Тесты для схем пользователя."""
    
    def test_user_update_request_valid(self):
        """Тест валидации запроса обновления."""
        # Валидные данные
        request = UserUpdateRequest(
            name="Иван Петров",
            phone="+79001234567",
            bio="Новое описание",
            language="ru",
        )
        assert request.name == "Иван Петров"
        assert request.phone == "+79001234567"
        assert request.bio == "Новое описание"
        assert request.language == "ru"
    
    def test_user_update_request_partial(self):
        """Тест частичного обновления."""
        request = UserUpdateRequest(name="Новое имя")
        assert request.name == "Новое имя"
        assert request.phone is None
        assert request.bio is None
    
    def test_user_update_request_name_strip(self):
        """Тест обрезки имени."""
        request = UserUpdateRequest(name="  Иван  ")
        assert request.name == "Иван"
    
    def test_user_update_request_phone_cleanup(self):
        """Тест очистки телефона."""
        request = UserUpdateRequest(phone="+7 900 123-45-67")
        assert request.phone == "+79001234567"


class TestUserServiceAuthorization:
    """Тесты проверки прав доступа в сервисе."""
    
    def test_owner_can_view_own_profile(self):
        """Тест: владелец может смотреть свой профиль."""
        user_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
        current_user = create_test_user(user_id=str(user_id))
        
        # Мок сессии
        mock_session = AsyncMock()
        
        with patch("app.services.users.service.UserRepository"):
            service = UserService(mock_session)
            
            result = service.check_can_view_profile(current_user, user_id)
            assert result is True
    
    def test_admin_can_view_any_profile(self):
        """Тест: админ может смотреть любой профиль."""
        target_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440001")
        admin = create_test_user(
            user_id="550e8400-e29b-41d4-a716-446655440000",
            role=UserRole.ADMIN,
        )
        
        mock_session = AsyncMock()
        
        with patch("app.services.users.service.UserRepository"):
            service = UserService(mock_session)
            
            result = service.check_can_view_profile(admin, target_id)
            assert result is True
    
    def test_user_cannot_view_other_profile(self):
        """Тест: пользователь не может смотреть чужой профиль."""
        current_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
        target_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440001")
        
        current_user = create_test_user(user_id=str(current_id))
        
        mock_session = AsyncMock()
        
        with patch("app.services.users.service.UserRepository"):
            service = UserService(mock_session)
            
            result = service.check_can_view_profile(current_user, target_id)
            # По умолчанию проверка вернет False для чужих профилей
            # (кроме случая когда это not active или blocked)
            assert result is False
    
    def test_blocked_user_cannot_view_profiles(self):
        """Тест: заблокированный пользователь не может смотреть профили."""
        current_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
        target_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440001")
        
        current_user = create_test_user(
            user_id=str(current_id),
            is_blocked=True,
        )
        
        mock_session = AsyncMock()
        
        with patch("app.services.users.service.UserRepository"):
            service = UserService(mock_session)
            
            result = service.check_can_view_profile(current_user, target_id)
            assert result is False


class TestUserServiceUpdate:
    """Тесты обновления профиля."""
    
    @pytest.mark.asyncio
    async def test_update_own_profile_success(self):
        """Тест: успешное обновление своего профиля."""
        user_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
        current_user = create_test_user(user_id=str(user_id))
        
        # Мок сессии и репозитория
        mock_session = AsyncMock()
        mock_repo = AsyncMock()
        mock_user = create_test_user(user_id=str(user_id))
        
        with patch.object(UserRepository, "get_user_by_id", return_value=mock_user):
            with patch.object(UserRepository, "update_user", return_value=mock_user):
                with patch.object(UserRepository, "get_user_with_reviews", return_value=(mock_user, [], 0)):
                    service = UserService(mock_session)
                    service.repository = mock_repo
                    
                    update_data = UserUpdateRequest(
                        name="Новое имя",
                        bio="Новое описание",
                    )
                    
                    # Это должно пройти без исключений
                    result = await service.update_user_profile(
                        current_user=current_user,
                        target_user_id=user_id,
                        update_data=update_data,
                        avatar_file=None,
                    )
                    # Проверяем, что результат - объект UserResponse
                    assert result is not None
    
    @pytest.mark.asyncio
    async def test_update_other_profile_forbidden(self):
        """Тест: нельзя редактировать чужой профиль."""
        current_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
        target_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440001")
        
        current_user = create_test_user(user_id=str(current_id))
        
        mock_session = AsyncMock()
        
        with patch("app.services.users.service.UserRepository"):
            service = UserService(mock_session)
            
            update_data = UserUpdateRequest(name="Хакер")
            
            with pytest.raises(HTTPException) as exc_info:
                await service.update_user_profile(
                    current_user=current_user,
                    target_user_id=target_id,
                    update_data=update_data,
                    avatar_file=None,
                )
            
            assert exc_info.value.status_code == 403
            assert "Not authorized" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_admin_can_update_any_profile(self):
        """Тест: админ может редактировать любой профиль."""
        admin_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
        target_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440001")
        
        admin = create_test_user(user_id=str(admin_id), role=UserRole.ADMIN)
        target_user = create_test_user(user_id=str(target_id))
        
        mock_session = AsyncMock()
        mock_repo = AsyncMock()
        
        with patch.object(UserRepository, "get_user_by_id", return_value=target_user):
            with patch.object(UserRepository, "update_user", return_value=target_user):
                with patch.object(UserRepository, "get_user_with_reviews", return_value=(target_user, [], 0)):
                    service = UserService(mock_session)
                    service.repository = mock_repo
                    
                    update_data = UserUpdateRequest(name="Новое имя")
                    
                    result = await service.update_user_profile(
                        current_user=admin,
                        target_user_id=target_id,
                        update_data=update_data,
                        avatar_file=None,
                    )
                    
                    assert result is not None


class TestAvatarUpload:
    """Тесты загрузки аватара."""
    
    @pytest.mark.asyncio
    async def test_invalid_avatar_type(self):
        """Тест: неверный тип файла."""
        user_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
        current_user = create_test_user(user_id=str(user_id))
        
        mock_session = AsyncMock()
        
        with patch("app.services.users.service.UserRepository"):
            service = UserService(mock_session)
            
            # Мок файла с неверным типом
            mock_file = AsyncMock()
            mock_file.content_type = "application/pdf"
            mock_file.file = MagicMock()
            mock_file.file.seek = MagicMock()
            mock_file.file.tell = MagicMock(return_value=1000)
            mock_file.read = AsyncMock(return_value=b"fake content")
            
            with pytest.raises(HTTPException) as exc_info:
                await service.update_user_profile(
                    current_user=current_user,
                    target_user_id=user_id,
                    update_data=UserUpdateRequest(),
                    avatar_file=mock_file,
                )
            
            assert exc_info.value.status_code == 400
            assert "Invalid file type" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_avatar_too_large(self):
        """Тест: файл слишком большой."""
        user_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
        current_user = create_test_user(user_id=str(user_id))
        
        mock_session = AsyncMock()
        
        with patch("app.services.users.service.UserRepository"):
            service = UserService(mock_session)
            
            # Мок файла с размером больше 10MB
            mock_file = AsyncMock()
            mock_file.content_type = "image/jpeg"
            mock_file.file = MagicMock()
            mock_file.file.seek = MagicMock()
            mock_file.file.tell = MagicMock(return_value=20 * 1024 * 1024)  # 20MB
            mock_file.read = AsyncMock(return_value=b"fake content")
            
            with pytest.raises(HTTPException) as exc_info:
                await service.update_user_profile(
                    current_user=current_user,
                    target_user_id=user_id,
                    update_data=UserUpdateRequest(),
                    avatar_file=mock_file,
                )
            
            assert exc_info.value.status_code == 400
            assert "File too large" in exc_info.value.detail


# Импорт для patch
from app.repositories.users.repository import UserRepository