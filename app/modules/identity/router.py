from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.platform.database import get_db
from app.platform.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.modules.identity.models import User
from app.modules.identity.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    TokenResponse,
    MeResponse,
    RoleUpdate,
)
from app.modules.identity.dependencies import get_current_user, get_current_workspace
from app.modules.workspaces.models import Workspace

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    user = User(
        email=str(data.email).lower(), password_hash=get_password_hash(data.password)
    )
    try:
        db.add(user)
        await db.flush()
        db.add(
            Workspace(
                name=data.workspace_name.strip() or "Мое пространство", owner_id=user.id
            )
        )
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(409, "Этот email уже зарегистрирован")
    return user


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    user = await db.scalar(select(User).where(User.email == str(data.email).lower()))
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Неверный email или пароль")
    return {"access_token": create_access_token({"sub": str(user.id)})}


@router.get("/me", response_model=MeResponse)
async def me(
    user: User = Depends(get_current_user),
    workspace: Workspace = Depends(get_current_workspace),
):
    return {
        "id": user.id,
        "email": user.email,
        "workspace_id": workspace.id,
        "workspace_name": workspace.name,
        "active_role": user.active_role,
    }


@router.patch("/me/role", response_model=MeResponse)
async def switch_role(
    data: RoleUpdate,
    user: User = Depends(get_current_user),
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db),
):
    # Both roles belong to the same account. This is a UI preference, never an ownership grant.
    user.active_role = data.active_role
    await db.commit()
    return await me(user, workspace)
