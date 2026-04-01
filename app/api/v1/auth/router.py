"""
Роутер домена Auth.
Эндпоинты:
- POST /register — регистрация
- POST /login — вход
- POST /logout — выход
- GET /me — текущий пользователь
- POST /refresh — обновление токена
- POST /password-reset — сброс пароля
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.auth import (
    ErrorDetail,
    LoginRequest,
    TokenResponse,
    UserRegisterRequest,
)
from app.services.auth.service import AuthService
from app.repositories.users.repository import UserRepository

router = APIRouter()


@router.post(
    "/register",
    response_model=TokenResponse,
    responses={
        400: {"model": ErrorDetail, "description": "Email уже зарегистрирован"},
        422: {"model": ErrorDetail, "description": "Невалидные данные"},
    },
    summary="Регистрация нового пользователя",
    description="Регистрирует нового пользователя с email и паролем. Возвращает JWT токен.",
)
async def register(
    data: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Регистрация нового пользователя.
    
    Принимает email, пароль и имя. Проверяет уникальность email,
    хэширует пароль и создаёт пользователя.
    
    Возвращает JWT токен доступа.
    """
    user_repository = UserRepository(db)
    auth_service = AuthService(user_repository)
    
    try:
        result = await auth_service.register_user(data)
        return result
    except ValueError as e:
        if str(e) == "Email already registered":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )


@router.post("/login")
async def login() -> dict[str, str]:
    """Вход в систему."""
    return {"message": "Login endpoint"}


@router.post("/logout")
async def logout() -> dict[str, str]:
    """Выход из системы."""
    return {"message": "Logout endpoint"}


@router.get("/me")
async def get_current_user() -> dict[str, str]:
    """Получение текущего пользователя."""
    return {"message": "Current user endpoint"}


@router.post("/refresh")
async def refresh_token() -> dict[str, str]:
    """Обновление access токена."""
    return {"message": "Refresh token endpoint"}


@router.post("/password-reset")
async def reset_password() -> dict[str, str]:
    """Запрос на сброс пароля."""
    return {"message": "Password reset endpoint"}