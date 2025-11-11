from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.notification import SyncNotification
from ..schemas.notification import NotificationRead
from .deps import get_current_user, get_db_session

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationRead])
async def list_notifications(
    session: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    query = select(SyncNotification).where(
        SyncNotification.user_id == current_user.id,
        SyncNotification.is_read.is_(False),
    ).order_by(SyncNotification.created_at.desc())
    result = await session.execute(query)
    return result.scalars().all()


@router.post("/{notification_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_notification_read(
    notification_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    notification = await session.get(SyncNotification, notification_id)
    if notification is None or notification.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    notification.is_read = True
    await session.commit()
