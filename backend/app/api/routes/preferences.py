from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.provider import get_ai_provider
from app.api.deps import get_current_user, get_db_dep
from app.schemas.auth import AuthUser
from app.schemas.preference import PreferenceResponse, PreferenceUpdate
from app.services.preference_service import PreferenceService

router = APIRouter(prefix="/preferences", tags=["preferences"])


@router.get("", response_model=PreferenceResponse)
async def get_preferences(
    current_user: AuthUser = Depends(get_current_user), db: AsyncSession = Depends(get_db_dep)
) -> PreferenceResponse:
    return await PreferenceService(db).get(current_user.id)


@router.put("", response_model=PreferenceResponse)
async def update_preferences(
    payload: PreferenceUpdate,
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_dep),
) -> PreferenceResponse:
    ai_provider = get_ai_provider()
    return await PreferenceService(db, ai_provider).upsert(current_user.id, payload)
