from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.provider import AIProvider
from app.core.exceptions import NotFoundError
from app.models.preference import Preference
from app.schemas.preference import PreferenceUpdate


def _preference_text(payload: PreferenceUpdate) -> str:
    """Flatten preferences into a single text blob for embedding."""
    parts = [
        "Roles: " + ", ".join(payload.preferred_roles),
        "Skills: " + ", ".join(payload.skills),
        "Locations: " + ", ".join(payload.preferred_locations),
        f"Remote only: {payload.remote_only}",
        f"Experience level: {payload.experience_level.value if payload.experience_level else 'any'}",
        f"Employment type: {payload.employment_type.value if payload.employment_type else 'any'}",
    ]
    return "\n".join(parts)


class PreferenceService:
    def __init__(self, db: AsyncSession, ai_provider: AIProvider | None = None):
        self.db = db
        self.ai_provider = ai_provider

    async def get(self, profile_id: uuid.UUID) -> Preference:
        result = await self.db.execute(select(Preference).where(Preference.profile_id == profile_id))
        pref = result.scalar_one_or_none()
        if pref is None:
            raise NotFoundError("Preferences not set for this profile yet")
        return pref

    async def upsert(self, profile_id: uuid.UUID, payload: PreferenceUpdate) -> Preference:
        result = await self.db.execute(select(Preference).where(Preference.profile_id == profile_id))
        pref = result.scalar_one_or_none()

        if pref is None:
            pref = Preference(profile_id=profile_id)
            self.db.add(pref)

        for field, value in payload.model_dump().items():
            setattr(pref, field, value)

        if self.ai_provider is not None:
            pref.embedding = await self.ai_provider.embed(_preference_text(payload))

        await self.db.commit()
        await self.db.refresh(pref)
        return pref
