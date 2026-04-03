"""
Сервис для работы с настройками пользователей.

Содержит бизнес-логику для:
- Получения настроек пользователя
- Обновления настроек пользователя
"""
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users.model import User
from app.models.users.settings import UserSettings
from app.repositories.users.settings import UserSettingsRepository
from app.schemas.users.settings import (
    UserSettingsResponse,
    UserSettingsUpdateRequest,
)


class UserSettingsService:
    """
    Сервис для работы с настройками пользователей.
    
    Обеспечивает бизнес-логику для работы с настройками.
    """
    
    def __init__(self, session: AsyncSession) -> None:
        """
        Инициализация сервиса.
        
        Args:
            session: Асинхронная сессия БД
        """
        self.session = session
        self.repository = UserSettingsRepository(session)
    
    async def get_settings(self, user_id: uuid.UUID) -> UserSettingsResponse:
        """
        Получение настроек пользователя.
        
        Если настроек нет - создает с дефолтными значениями.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            UserSettingsResponse: Настройки пользователя
        """
        settings = await self.repository.get_user_settings(user_id)
        
        if not settings:
            # Создаем настройки с дефолтными значениями
            settings = await self.repository.create_user_settings(user_id)
            await self.repository.commit()
        
        return UserSettingsResponse(
            id=str(settings.id),
            user_id=str(settings.user_id),
            language=settings.language,
            timezone=settings.timezone,
            theme=settings.theme,
            notifications_enabled=settings.notifications_enabled,
            email_notifications=settings.email_notifications,
            push_notifications=settings.push_notifications,
            telegram_notifications=settings.telegram_notifications,
            trip_request_notifications=settings.trip_request_notifications,
            message_notifications=settings.message_notifications,
            review_notifications=settings.review_notifications,
            marketing_notifications=settings.marketing_notifications,
            privacy_show_profile=settings.privacy_show_profile,
            privacy_show_phone=settings.privacy_show_phone,
            privacy_show_last_seen=settings.privacy_show_last_seen,
            created_at=settings.created_at,
            updated_at=settings.updated_at,
        )
    
    async def update_settings(
        self,
        user_id: uuid.UUID,
        update_data: UserSettingsUpdateRequest,
    ) -> UserSettingsResponse:
        """
        Обновление настроек пользователя.
        
        Если настроек нет - создает с указанными значениями.
        
        Args:
            user_id: ID пользователя
            update_data: Данные для обновления
            
        Returns:
            UserSettingsResponse: Обновленные настройки
        """
        settings = await self.repository.get_user_settings(user_id)
        
        if not settings:
            # Создаем новые настройки
            settings = await self.repository.create_user_settings(
                user_id,
                update_data.model_dump(exclude_none=True),
            )
            await self.repository.commit()
        else:
            # Обновляем существующие настройки
            settings = await self.repository.update_user_settings(
                settings,
                update_data.model_dump(exclude_none=True),
            )
            await self.repository.commit()
        
        return UserSettingsResponse(
            id=str(settings.id),
            user_id=str(settings.user_id),
            language=settings.language,
            timezone=settings.timezone,
            theme=settings.theme,
            notifications_enabled=settings.notifications_enabled,
            email_notifications=settings.email_notifications,
            push_notifications=settings.push_notifications,
            telegram_notifications=settings.telegram_notifications,
            trip_request_notifications=settings.trip_request_notifications,
            message_notifications=settings.message_notifications,
            review_notifications=settings.review_notifications,
            marketing_notifications=settings.marketing_notifications,
            privacy_show_profile=settings.privacy_show_profile,
            privacy_show_phone=settings.privacy_show_phone,
            privacy_show_last_seen=settings.privacy_show_last_seen,
            created_at=settings.created_at,
            updated_at=settings.updated_at,
        )