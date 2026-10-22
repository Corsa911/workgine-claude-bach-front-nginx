from datetime import datetime
from typing import Literal
import uuid
from pydantic import BaseModel, ConfigDict, Field


class OrderCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    category_id: uuid.UUID | None = None
    title: str = Field(min_length=3, max_length=255)
    description: str = Field(min_length=1, max_length=20000)
    budget_minor: int = Field(default=0, ge=0, le=2000000000)


class OrderUpdate(OrderCreate):
    version: int = Field(ge=1)


class OrderPublish(BaseModel):
    version: int = Field(ge=1)


class OrderResponse(BaseModel):
    id: uuid.UUID
    customer_workspace_id: uuid.UUID
    category_id: uuid.UUID | None
    title: str
    description: str
    budget_minor: int
    currency: Literal["KZT"] = "KZT"
    status: str
    visibility: str
    version: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
