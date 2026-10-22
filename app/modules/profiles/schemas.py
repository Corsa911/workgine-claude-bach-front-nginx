import uuid
from pydantic import BaseModel, ConfigDict, Field


class ExecutorProfileUpsert(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    description: str = Field(default="", max_length=10000)
    hourly_rate_minor: int = Field(default=0, ge=0, le=2000000000)


class ExecutorProfileResponse(ExecutorProfileUpsert):
    workspace_id: uuid.UUID
    publication_status: str
    model_config = ConfigDict(from_attributes=True)
