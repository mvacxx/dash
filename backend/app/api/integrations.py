from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.integration import IntegrationAccount, IntegrationType
from ..schemas.integration import (
    AdSenseIntegrationCreate,
    FacebookIntegrationCreate,
    IntegrationRead,
)
from .deps import get_db_session, get_existing_user

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.post("/facebook/{user_id}", response_model=IntegrationRead, status_code=status.HTTP_201_CREATED)
async def connect_facebook(
    user_id: int,
    payload: FacebookIntegrationCreate,
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_existing_user),
):
    del user  # Only ensure user exists
    credentials = payload.dict(exclude_none=True)
    api_version = credentials.pop("api_version", "v18.0")

    integration = IntegrationAccount(
        user_id=user_id,
        type=IntegrationType.FACEBOOK,
        credentials={**credentials, "api_version": api_version},
    )
    session.add(integration)
    await session.commit()
    await session.refresh(integration)
    return integration


@router.post("/adsense/{user_id}", response_model=IntegrationRead, status_code=status.HTTP_201_CREATED)
async def connect_adsense(
    user_id: int,
    payload: AdSenseIntegrationCreate,
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_existing_user),
):
    del user
    integration = IntegrationAccount(
        user_id=user_id,
        type=IntegrationType.ADSENSE,
        credentials={"account_id": payload.account_id, **payload.dict(exclude={"account_id"})},
    )
    session.add(integration)
    await session.commit()
    await session.refresh(integration)
    return integration


@router.get("/{user_id}", response_model=list[IntegrationRead])
async def list_integrations(
    user_id: int,
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_existing_user),
):
    del user
    result = await session.execute(
        select(IntegrationAccount).where(IntegrationAccount.user_id == user_id)
    )
    return result.scalars().all()
