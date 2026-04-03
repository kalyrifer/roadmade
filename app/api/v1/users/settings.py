"""
Роутер для настроек пользователя.

Эндпоинты:
- GET /users/settings — получение настроек
- PUT /users/settings — обновление настроек
"""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.users.model import User
from app.schemas.users.settings import (
    UserSettingsResponse,
    UserSettingsUpdateRequest,
)
from app.services.users.settings import UserSettingsService

router = APIRouter()


async def get_settings_service(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> UserSettingsService:
    """
    Получение сервиса настроек пользователей.
    
    Args:
        db: Сессия БД
        
    Returns:
        UserSettingsService: Экземпляр сервиса
    """
    return UserSettingsService(db)


# Типы для зависимостей
SettingsServiceDep = Annotated[UserSettingsService, Depends(get_settings_service)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]


@router.get("/settings", response_model=UserSettingsResponse)
async def get_user_settings(
    current_user: CurrentUserDep,
    settings_service: SettingsServiceDep,
) -> UserSettingsResponse:
    """
    Получение настроек текущего пользователя.
    
    Protected route - требует авторизации.
    
    Args:
        current_user: Текущий авторизованный пользователь
        settings_service: Сервис настроек
        
    Returns:
        UserSettingsResponse: Настройки пользователя
    """
    return await settings_service.get_settings(current_user.id)


@router.put("/settings", response_model=UserSettingsResponse)
async def update_user_settings(
    current_user: CurrentUserDep,
    update_data: UserSettingsUpdateRequest,
    settings_service: SettingsServiceDep,
) -> UserSettingsResponse:
    """
    Обновление настроек текущего пользователя.
    
    Protected route - требует авторизации.
    Поддерживает частичное обновление полей.
    
    Args:
        current_user: Текущий авторизованный пользователь
        update_data: Данные для обновления
        settings_service: Сервис настроек
        
    Returns:
        UserSettingsResponse: Обновленные настройки
    """
    return await settings_service.update_settings(
        user_id=current_user.id,
        update_data=update_data,
    )