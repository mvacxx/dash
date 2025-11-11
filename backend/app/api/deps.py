from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_session
from ..models.user import User
from ..services.metrics import get_user


async def get_db_session() -> AsyncSession:
    async for session in get_session():
        yield session


async def get_existing_user(
    user_id: int, session: AsyncSession = Depends(get_db_session)
) -> User:
    user = await get_user(session, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
