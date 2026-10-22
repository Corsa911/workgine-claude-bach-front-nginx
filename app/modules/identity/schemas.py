import uuid
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field

Role = Literal["customer", "executor"]


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    workspace_name: str = Field(
        default="Мое пространство", min_length=1, max_length=255
    )


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    model_config = ConfigDict(from_attributes=True)


class RoleUpdate(BaseModel):
    active_role: Role


class MeResponse(UserResponse):
    workspace_id: uuid.UUID
    workspace_name: str
    active_role: Role | None
    available_roles: list[Role] = ["customer", "executor"]
