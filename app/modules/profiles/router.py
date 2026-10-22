from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.platform.database import get_db
from app.modules.identity.dependencies import get_current_workspace
from app.modules.workspaces.models import Workspace
from app.modules.profiles.models import ExecutorProfile
from app.modules.profiles.schemas import ExecutorProfileUpsert, ExecutorProfileResponse

router = APIRouter()


@router.get("/me", response_model=ExecutorProfileResponse)
async def get_profile(
    db: AsyncSession = Depends(get_db), ws: Workspace = Depends(get_current_workspace)
):
    profile = await db.get(ExecutorProfile, ws.id)
    return profile or {
        "workspace_id": ws.id,
        "description": "",
        "hourly_rate_minor": 0,
        "publication_status": "draft",
    }


@router.put("/me", response_model=ExecutorProfileResponse)
async def save_profile(
    payload: ExecutorProfileUpsert,
    db: AsyncSession = Depends(get_db),
    ws: Workspace = Depends(get_current_workspace),
):
    profile = await db.get(ExecutorProfile, ws.id)
    if not profile:
        profile = ExecutorProfile(workspace_id=ws.id)
        db.add(profile)
    profile.description = payload.description
    profile.hourly_rate_minor = payload.hourly_rate_minor
    await db.commit()
    await db.refresh(profile)
    return profile
