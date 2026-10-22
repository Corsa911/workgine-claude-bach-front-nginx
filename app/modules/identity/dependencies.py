import uuid
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.platform.database import get_db
from app.platform.config import settings
from app.platform.security import ALGORITHM
from app.modules.identity.models import User
from app.modules.workspaces.models import Workspace

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id = uuid.UUID(payload["sub"])
    except (JWTError, ValueError, TypeError, KeyError):
        raise HTTPException(
            401, "Войдите в аккаунт заново", headers={"WWW-Authenticate": "Bearer"}
        )
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(401, "Аккаунт не найден")
    return user


async def get_current_workspace(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Workspace:
    workspace = await db.scalar(select(Workspace).where(Workspace.owner_id == user.id))
    if not workspace:
        raise HTTPException(409, "У аккаунта нет рабочего пространства")
    return workspace
