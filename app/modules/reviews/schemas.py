import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ReviewCreate(BaseModel):
    order_id: uuid.UUID
    target_workspace_id: uuid.UUID
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = None


class ReviewResponse(BaseModel):
    id: uuid.UUID
    order_id: uuid.UUID
    author_workspace_id: uuid.UUID
    target_workspace_id: uuid.UUID
    rating: int
    comment: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
