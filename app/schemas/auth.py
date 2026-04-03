"""
Схемы для аутентификации и авторизации.

Содержит Pydantic схемы для:
- Регистрации пользователя
- Входа в систему
- Ответов с токенами
"""
import re
from datetime import datetime
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)


class UserRegisterRequest(BaseModel):
    """
    Схема для регистрации нового пользователя.
    
    Валидирует email, пароль и имя.
    """
    email: str = Field(
        ...,
        description="Email пользователя",
        examples=["user@example.com"],
    )
    password: str = Field(
        ...,
        description="Пароль пользователя (минимум 6 символов)",
        min_length=6,
        examples=["securePassword123"],
    )
    name: str = Field(
        ...,
        description="Имя пользователя",
        min_length=1,
        max_length=100,
        examples=["Иван"],
    )

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        """
        Валидация и нормализация email.
        
        - Приводит к нижнему регистру
        - Убирает лишние пробелы
        
        Args:
            v: Email для валидации
            
        Returns:
            Нормализованный email
            
        Raises:
            ValueError: Если email некорректен
        """
        # Убираем пробелы
        v = v.strip()
        # Проверяем базовый формат email
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, v):
            raise ValueError("Invalid email format")
        return v.lower()

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """
        Валидация имени.
        
        - Убирает лишние пробелы
        
        Args:
            v: Имя для валидации
            
        Returns:
            Нормализованное имя
        """
        return v.strip()

    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "title": "UserRegisterRequest",
            "description": "Схема запроса на регистрацию пользователя",
        },
    )


class UserResponse(BaseModel):
    """
    Схема ответа с данными пользователя.
    
    Не включает чувствительные данные (пароль, хэш).
    """
    id: str = Field(..., description="Уникальный идентификатор пользователя")
    email: str = Field(..., description="Email пользователя")
    name: str = Field(..., description="Имя пользователя")
    rating_average: float = Field(
        default=0.0,
        description="Средний рейтинг пользователя",
    )
    rating_count: int = Field(
        default=0,
        description="Количество отзывов",
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "title": "UserResponse",
            "description": "Схема ответа с данными пользователя",
        },
    )


class TokenResponse(BaseModel):
    """
    Схема ответа с токеном доступа.
    
    Возвращается после успешной регистрации или входа.
    """
    access_token: str = Field(..., description="JWT токен доступа")
    token_type: str = Field(
        default="bearer",
        description="Тип токена",
    )
    user: UserResponse = Field(..., description="Данные пользователя")

    model_config = ConfigDict(
        json_schema_extra={
            "title": "TokenResponse",
            "description": "Схема ответа с токеном доступа",
        },
    )


class LoginRequest(BaseModel):
    """
    Схема для входа в систему.
    """
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., description="Пароль пользователя")

    model_config = ConfigDict(
        json_schema_extra={
            "title": "LoginRequest",
            "description": "Схема запроса на вход в систему",
        },
    )


class ErrorDetail(BaseModel):
    """
    Схема для ошибок.
    """
    detail: str = Field(..., description="Сообщение об ошибке")

    model_config = ConfigDict(
        json_schema_extra={
            "title": "ErrorDetail",
            "description": "Схема для ошибок API",
        },
    )