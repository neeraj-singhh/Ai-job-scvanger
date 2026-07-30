from fastapi import APIRouter, Depends
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_dep
from app.models.matching import NotificationHistory
from app.schemas.auth import AuthUser
from app.schemas.notification import NotificationResponse

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationResponse])
async def list_notifications(
    current_user: AuthUser = Depends(get_current_user), db: AsyncSession = Depends(get_db_dep)
) -> list[NotificationResponse]:
    stmt = (
        select(NotificationHistory)
        .where(NotificationHistory.profile_id == current_user.id)
        .order_by(NotificationHistory.created_at.desc())
        .limit(100)
    )
    return list((await db.execute(stmt)).scalars().all())


@router.post("/{notification_id}/read", status_code=204)
async def mark_read(
    notification_id: str,
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_dep),
) -> None:
    import uuid

    stmt = (
        update(NotificationHistory)
        .where(
            NotificationHistory.id == uuid.UUID(notification_id),
            NotificationHistory.profile_id == current_user.id,
        )
        .values(read=True)
    )
    await db.execute(stmt)
    await db.commit()
