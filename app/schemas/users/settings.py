"""
Схемы для настроек пользователя.

Содержит Pydantic схемы для:
- Ответа с настройками пользователя
- Обновления настроек пользователя
"""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserSettingsResponse(BaseModel):
    """
    Схема ответа с настройками пользователя.
    
    Используется для возврата настроек профиля.
    """
    id: str = Field(..., description="Уникальный идентификатор настроек")
    user_id: str = Field(..., description="ID пользователя")
    language: str = Field(
        default="ru",
        description="Язык интерфейса (ru, en)",
    )
    timezone: str = Field(
        default="Europe/Moscow",
        description="Часовой пояс",
    )
    theme: str = Field(
        default="light",
        description="Тема оформления (light, dark)",
    )
    
    # Настройки уведомлений
    notifications_enabled: bool = Field(
        default=True,
        description="Включены ли уведомления",
    )
    email_notifications: bool = Field(
        default=True,
        description="Уведомления на email",
    )
    push_notifications: bool = Field(
        default=True,
        description="Push-уведомления",
    )
    telegram_notifications: bool = Field(
        default=False,
        description="Уведомления в Telegram",
    )
    trip_request_notifications: bool = Field(
        default=True,
        description="Уведомления о заявках",
    )
    message_notifications: bool = Field(
        default=True,
        description="Уведомления о сообщениях",
    )
    review_notifications: bool = Field(
        default=True,
        description="Уведомления об отзывах",
    )
    marketing_notifications: bool = Field(
        default=False,
        description="Маркетинговые уведомления",
    )
    
    # Настройки приватности
    privacy_show_profile: bool = Field(
        default=True,
        description="Показывать профиль",
    )
    privacy_show_phone: bool = Field(
        default=True,
        description="Показывать телефон",
    )
    privacy_show_last_seen: bool = Field(
        default=True,
        description="Показывать последний визит",
    )
    
    created_at: datetime = Field(..., description="Время создания")
    updated_at: datetime = Field(..., description="Время последнего обновления")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "title": "UserSettingsResponse",
            "description": "Схема ответа с настройками пользователя",
        },
    )


class UserSettingsUpdateRequest(BaseModel):
    """
    Схема для обновления настроек пользователя.
    
    Поддерживает частичное обновление полей.
    """
    language: str | None = Field(
        None,
        description="Язык интерфейса (ru, en)",
        pattern=r"^(ru|en)$",
    )
    timezone: str | None = Field(
        None,
        description="Часовой пояс",
        max_length=50,
    )
    theme: str | None = Field(
        None,
        description="Тема оформления (light, dark)",
        pattern=r"^(light|dark)$",
    )
    
    # Настройки уведомлений
    notifications_enabled: bool | None = Field(
        None,
        description="Включены ли уведомления",
    )
    email_notifications: bool | None = Field(
        None,
        description="Уведомления на email",
    )
    push_notifications: bool | None = Field(
        None,
        description="Push-уведомления",
    )
    telegram_notifications: bool | None = Field(
        None,
        description="Уведомления в Telegram",
    )
    trip_request_notifications: bool | None = Field(
        None,
        description="Уведомления о заявках",
    )
    message_notifications: bool | None = Field(
        None,
        description="Уведомления о сообщениях",
    )
    review_notifications: bool | None = Field(
        None,
        description="Уведомления об отзывах",
    )
    marketing_notifications: bool | None = Field(
        None,
        description="Маркетинговые уведомления",
    )
    
    # Настройки приватности
    privacy_show_profile: bool | None = Field(
        None,
        description="Показывать профиль",
    )
    privacy_show_phone: bool | None = Field(
        None,
        description="Показывать телефон",
    )
    privacy_show_last_seen: bool | None = Field(
        None,
        description="Показывать последний визит",
    )

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str | None) -> str | None:
        """
        Валидация языка.
        
        Args:
            v: Язык для валидации
            
        Returns:
            str | None: Нормализованный язык или None
        """
        if v is not None:
            v = v.lower().strip()
            if v not in ("ru", "en"):
                raise ValueError("Language must be 'ru' or 'en'")
        return v

    @field_validator("theme")
    @classmethod
    def validate_theme(cls, v: str | None) -> str | None:
        """
        Валидация темы.
        
        Args:
            v: Тема для валидации
            
        Returns:
            str | None: Нормализованная тема или None
        """
        if v is not None:
            v = v.lower().strip()
            if v not in ("light", "dark"):
                raise ValueError("Theme must be 'light' or 'dark'")
        return v

    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "title": "UserSettingsUpdateRequest",
            "description": "Схема для обновления настроек пользователя",
        },
    )