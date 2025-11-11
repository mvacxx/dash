from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.integration import IntegrationAccount, IntegrationType
from ..schemas.integration import (
    AdSenseIntegrationCreate,
    FacebookIntegrationCreate,
    IntegrationRead,
)
from .deps import get_current_user, get_db_session

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.post("/facebook", response_model=IntegrationRead, status_code=status.HTTP_201_CREATED)
async def connect_facebook(
    payload: FacebookIntegrationCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    credentials = payload.dict(exclude_none=True)
    api_version = credentials.pop("api_version", "v18.0")

    integration = IntegrationAccount(
        user_id=current_user.id,
        type=IntegrationType.FACEBOOK,
        credentials={**credentials, "api_version": api_version},
    )
    session.add(integration)
    await session.commit()
    await session.refresh(integration)
    return integration


@router.post("/adsense", response_model=IntegrationRead, status_code=status.HTTP_201_CREATED)
async def connect_adsense(
    payload: AdSenseIntegrationCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    credentials = {
        "account_id": payload.account_id,
        "access_token": payload.access_token,
        "refresh_token": payload.refresh_token,
        "client_id": payload.client_id,
        "client_secret": payload.client_secret,
    }

    expiry: datetime | None = None
    if payload.token_expiry:
        expiry = payload.token_expiry
    elif payload.expires_in:
        expiry = datetime.now(timezone.utc) + timedelta(seconds=payload.expires_in)

    if expiry is not None:
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        credentials["token_expiry"] = expiry.astimezone(timezone.utc).isoformat()

    integration = IntegrationAccount(
        user_id=current_user.id,
        type=IntegrationType.ADSENSE,
        credentials=credentials,
    )
    session.add(integration)
    await session.commit()
    await session.refresh(integration)
    return integration


@router.get("", response_model=list[IntegrationRead])
async def list_integrations(
    session: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    result = await session.execute(
        select(IntegrationAccount).where(IntegrationAccount.user_id == current_user.id)
    )
    return result.scalars().all()
