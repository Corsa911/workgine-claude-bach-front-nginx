import uuid
from typing import List
from fastapi import (
    APIRouter,
    Depends,
    WebSocket,
    WebSocketDisconnect,
    status,
    HTTPException,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.platform.database import get_db, async_session_maker
from app.modules.chat.models import ChatRoom, Message
from app.modules.chat.schemas import ChatRoomResponse, MessageResponse, MessageCreate
from app.modules.chat.manager import manager
from app.modules.identity.dependencies import get_current_user
from app.modules.identity.models import User
from app.modules.workspaces.models import Workspace

router = APIRouter(tags=["Chat & WebSockets"])


@router.post(
    "/rooms/", response_model=ChatRoomResponse, status_code=status.HTTP_201_CREATED
)
async def create_chat_room(
    order_id: uuid.UUID | None = None, db: AsyncSession = Depends(get_db)
):
    """Создать новую комнату чата (например, при отклике или заказе)"""
    room = ChatRoom(order_id=order_id)
    db.add(room)
    await db.commit()
    await db.refresh(room)
    return room


@router.get("/rooms/{room_id}/messages", response_model=List[MessageResponse])
async def get_room_messages(room_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Получить историю сообщений комнаты"""
    result = await db.execute(
        select(Message)
        .where(Message.room_id == room_id)
        .order_by(Message.created_at.asc())
    )
    return result.scalars().all()


@router.websocket("/ws/{room_id}")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    room_id: str,
    token: str,  # Передается в query параметрах: ws://.../ws/{room_id}?token=JWT_TOKEN
):
    """WebSocket эндпоинт для обмена сообщениями в реальном времени с JWT аутентификацией"""
    from jose import jwt, JWTError
    from app.platform.security import ALGORITHM
    from app.platform.config import settings

    # 1. Валидация JWT токена и определение пользователя/воркспейса
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id = uuid.UUID(payload["sub"])
        if not user_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    except (JWTError, ValueError, KeyError, TypeError):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Получаем сессию БД для WebSocket
    async with async_session_maker() as db:
        user_res = await db.execute(select(User).where(User.id == user_id))
        user = user_res.scalars().first()
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        ws_res = await db.execute(
            select(Workspace).where(Workspace.owner_id == user.id)
        )
        workspace = ws_res.scalars().first()
        if not workspace:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        workspace_id = workspace.id

    # 2. Подключение к менеджеру чата
    await manager.connect(room_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            content = data.get("content")
            if not content:
                continue

            # 3. Сохранение сообщения в базу данных
            async with async_session_maker() as db:
                new_message = Message(
                    room_id=uuid.UUID(room_id),
                    sender_workspace_id=workspace_id,
                    content=content,
                )
                db.add(new_message)
                await db.commit()
                await db.refresh(new_message)

                message_data = {
                    "id": str(new_message.id),
                    "room_id": str(new_message.room_id),
                    "sender_workspace_id": str(new_message.sender_workspace_id),
                    "content": new_message.content,
                    "created_at": new_message.created_at.isoformat(),
                }

            # 4. Рассылка сообщения всем участникам комнаты
            await manager.broadcast(room_id, message_data)

    except WebSocketDisconnect:
        manager.disconnect(room_id, websocket)
