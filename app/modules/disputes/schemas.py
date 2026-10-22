import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from app.modules.disputes.models import DisputeStatus


class DisputeCreate(BaseModel):
    order_id: uuid.UUID
    reason: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=10)


class DisputeResolve(BaseModel):
    status: DisputeStatus  # RESOLVED_REFUND или RESOLVED_PAYOUT
    resolution_comment: str = Field(..., min_length=5)


class DisputeResponse(BaseModel):
    id: uuid.UUID
    order_id: uuid.UUID
    initiator_workspace_id: uuid.UUID
    reason: str
    description: str
    status: DisputeStatus
    resolution_comment: str | None
    created_at: datetime

    class Config:
        from_attributes = True
