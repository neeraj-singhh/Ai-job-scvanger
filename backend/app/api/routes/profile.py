from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_dep
from app.core.exceptions import NotFoundError
from app.models.profile import Profile
from app.schemas.auth import AuthUser
from app.schemas.notification import ProfileResponse, ProfileUpdate

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ProfileResponse)
async def get_profile(
    current_user: AuthUser = Depends(get_current_user), db: AsyncSession = Depends(get_db_dep)
) -> Profile:
    profile = await db.get(Profile, current_user.id)
    if profile is None:
        raise NotFoundError("Profile not found")
    return profile


@router.put("", response_model=ProfileResponse)
async def update_profile(
    payload: ProfileUpdate,
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_dep),
) -> Profile:
    profile = await db.get(Profile, current_user.id)
    if profile is None:
        raise NotFoundError("Profile not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)

    await db.commit()
    await db.refresh(profile)
    return profile
