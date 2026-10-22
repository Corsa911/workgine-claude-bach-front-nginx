import uuid
from pydantic import BaseModel, ConfigDict


class CategoryCreate(BaseModel):
    name: str
    slug: str
    parent_id: uuid.UUID | None = None


class CategoryResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    parent_id: uuid.UUID | None = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class SkillCreate(BaseModel):
    name: str
    slug: str


class SkillResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str

    model_config = ConfigDict(from_attributes=True)
