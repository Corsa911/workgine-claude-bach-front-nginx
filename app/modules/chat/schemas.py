import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1)


class MessageResponse(BaseModel):
    id: uuid.UUID
    room_id: uuid.UUID
    sender_workspace_id: uuid.UUID
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatRoomResponse(BaseModel):
    id: uuid.UUID
    order_id: uuid.UUID | None
    created_at: datetime

    class Config:
        from_attributes = True
