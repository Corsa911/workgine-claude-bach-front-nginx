import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.modules.applications.models import ApplicationStatus


class ApplicationCreate(BaseModel):
    order_id: uuid.UUID
    freelancer_workspace_id: uuid.UUID
    cover_letter: str
    bid_amount_minor: int
    currency: str = "USD"


class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus


class ApplicationResponse(BaseModel):
    id: uuid.UUID
    order_id: uuid.UUID
    freelancer_workspace_id: uuid.UUID
    cover_letter: str
    bid_amount_minor: int
    currency: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
