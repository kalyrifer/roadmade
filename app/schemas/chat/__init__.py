"""
Pydantic схемы для чатов (Chat).

Экспорты:
- ConversationCreate — создание чата
- ConversationRead — чтение чата
- ConversationList — список чатов с пагинацией
- ConversationCreateResponse — ответ при создании чата
- MessageCreate — создание сообщения
- MessageRead — чтение сообщения
- MessageList — список сообщений с пагинацией
- MessageCreateResponse — ответ при отправке сообщения
- ConversationParticipantRead — чтение участника чата
- ConversationMuteUpdate — управление уведомлениями
- WebSocketMessage — сообщение для WebSocket
- WebSocketConnection — подключение для WebSocket
"""
from app.schemas.chat.schemas import (
    ConversationByTripCreate,
    ConversationCreate,
    ConversationCreateResponse,
    ConversationList,
    ConversationMuteUpdate,
    ConversationParticipantRead,
    ConversationRead,
    MessageCreate,
    MessageCreateResponse,
    MessageList,
    MessageRead,
    MessageReadUpdate,
    TripBrief,
    UserBrief,
    WebSocketConnection,
    WebSocketMessage,
)

__all__ = [
    "ConversationByTripCreate",
    "ConversationCreate",
    "ConversationCreateResponse",
    "ConversationList",
    "ConversationMuteUpdate",
    "ConversationParticipantRead",
    "ConversationRead",
    "MessageCreate",
    "MessageCreateResponse",
    "MessageList",
    "MessageRead",
    "MessageReadUpdate",
    "TripBrief",
    "UserBrief",
    "WebSocketConnection",
    "WebSocketMessage",
]
