"""
Репозиторий для работы с настройками пользователей.

Содержит асинхронные методы для:
- Получения настроек пользователя
- Создания/обновления настроек пользователя
"""
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users.settings import UserSettings


class UserSettingsRepository:
    """
    Репозиторий для работы с настройками пользователей.
    
    Обеспечивает доступ к данным настроек в БД.
    """
    
    def __init__(self, session: AsyncSession) -> None:
        """
        Инициализация репозитория.
        
        Args:
            session: Асинхронная сессия БД
        """
        self.session = session
    
    async def get_user_settings(self, user_id: uuid.UUID) -> UserSettings | None:
        """
        Получение настроек пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            UserSettings | None: Найденные настройки или None
        """
        stmt = select(UserSettings).where(UserSettings.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create_user_settings(
        self,
        user_id: uuid.UUID,
        settings_data: dict[str, Any] | None = None,
    ) -> UserSettings:
        """
        Создание настроек пользователя.
        
        Args:
            user_id: ID пользователя
            settings_data: Словарь с данными настроек (опционально)
            
        Returns:
            UserSettings: Созданные настройки
        """
        if settings_data is None:
            settings_data = {}
        
        settings = UserSettings(
            user_id=user_id,
            language=settings_data.get("language", "ru"),
            timezone=settings_data.get("timezone", "Europe/Moscow"),
            theme=settings_data.get("theme", "light"),
            notifications_enabled=settings_data.get("notifications_enabled", True),
            email_notifications=settings_data.get("email_notifications", True),
            push_notifications=settings_data.get("push_notifications", True),
            telegram_notifications=settings_data.get("telegram_notifications", False),
            trip_request_notifications=settings_data.get("trip_request_notifications", True),
            message_notifications=settings_data.get("message_notifications", True),
            review_notifications=settings_data.get("review_notifications", True),
            marketing_notifications=settings_data.get("marketing_notifications", False),
            privacy_show_profile=settings_data.get("privacy_show_profile", True),
            privacy_show_phone=settings_data.get("privacy_show_phone", True),
            privacy_show_last_seen=settings_data.get("privacy_show_last_seen", True),
        )
        
        self.session.add(settings)
        await self.session.flush()
        await self.session.refresh(settings)
        return settings
    
    async def update_user_settings(
        self,
        settings: UserSettings,
        update_data: dict[str, Any],
    ) -> UserSettings:
        """
        Обновление настроек пользователя.
        
        Обновляет только переданные поля.
        
        Args:
            settings: Настройки для обновления
            update_data: Словарь с данными для обновления
            
        Returns:
            UserSettings: Обновленные настройки
        """
        # Настройки интерфейса
        if "language" in update_data and update_data["language"] is not None:
            settings.language = update_data["language"]
        if "timezone" in update_data and update_data["timezone"] is not None:
            settings.timezone = update_data["timezone"]
        if "theme" in update_data and update_data["theme"] is not None:
            settings.theme = update_data["theme"]
        
        # Настройки уведомлений
        if "notifications_enabled" in update_data and update_data["notifications_enabled"] is not None:
            settings.notifications_enabled = update_data["notifications_enabled"]
        if "email_notifications" in update_data and update_data["email_notifications"] is not None:
            settings.email_notifications = update_data["email_notifications"]
        if "push_notifications" in update_data and update_data["push_notifications"] is not None:
            settings.push_notifications = update_data["push_notifications"]
        if "telegram_notifications" in update_data and update_data["telegram_notifications"] is not None:
            settings.telegram_notifications = update_data["telegram_notifications"]
        if "trip_request_notifications" in update_data and update_data["trip_request_notifications"] is not None:
            settings.trip_request_notifications = update_data["trip_request_notifications"]
        if "message_notifications" in update_data and update_data["message_notifications"] is not None:
            settings.message_notifications = update_data["message_notifications"]
        if "review_notifications" in update_data and update_data["review_notifications"] is not None:
            settings.review_notifications = update_data["review_notifications"]
        if "marketing_notifications" in update_data and update_data["marketing_notifications"] is not None:
            settings.marketing_notifications = update_data["marketing_notifications"]
        
        # Настройки приватности
        if "privacy_show_profile" in update_data and update_data["privacy_show_profile"] is not None:
            settings.privacy_show_profile = update_data["privacy_show_profile"]
        if "privacy_show_phone" in update_data and update_data["privacy_show_phone"] is not None:
            settings.privacy_show_phone = update_data["privacy_show_phone"]
        if "privacy_show_last_seen" in update_data and update_data["privacy_show_last_seen"] is not None:
            settings.privacy_show_last_seen = update_data["privacy_show_last_seen"]
        
        await self.session.flush()
        await self.session.refresh(settings)
        return settings
    
    async def commit(self) -> None:
        """Коммит транзакции."""
        await self.session.commit()
    
    async def rollback(self) -> None:
        """Откат транзакции."""
        await self.session.rollback()