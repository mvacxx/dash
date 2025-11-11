from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.integration import IntegrationAccount, IntegrationType
from ..schemas.integration import (
    AdSenseIntegrationCreate,
    FacebookIntegrationCreate,
    AdSenseIntegrationUpdate,
    FacebookIntegrationUpdate,
    IntegrationRead,
)
from .deps import get_current_user, get_db_session

router = APIRouter(prefix="/integrations", tags=["integrations"])


async def _get_integration_for_user(
    session: AsyncSession, user_id: int, integration_id: int
) -> IntegrationAccount:
    integration = await session.get(IntegrationAccount, integration_id)
    if integration is None or integration.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Integration not found")
    return integration


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


@router.put("/facebook/{integration_id}", response_model=IntegrationRead)
async def update_facebook(
    integration_id: int,
    payload: FacebookIntegrationUpdate,
    session: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    integration = await _get_integration_for_user(session, current_user.id, integration_id)
    if integration.type != IntegrationType.FACEBOOK:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Integration type mismatch",
        )

    existing_credentials = dict(integration.credentials)
    data = payload.dict(exclude_unset=True)

    if "account_id" in data and data["account_id"]:
        existing_credentials["account_id"] = data["account_id"]
    if "access_token" in data and data["access_token"]:
        existing_credentials["access_token"] = data["access_token"]
    if "business_id" in data:
        business_id = data["business_id"] or None
        if business_id is None and "business_id" in existing_credentials:
            existing_credentials.pop("business_id")
        else:
            existing_credentials["business_id"] = business_id
    if "api_version" in data and data["api_version"]:
        existing_credentials["api_version"] = data["api_version"]

    integration.credentials = existing_credentials
    await session.commit()
    await session.refresh(integration)
    return integration


@router.put("/adsense/{integration_id}", response_model=IntegrationRead)
async def update_adsense(
    integration_id: int,
    payload: AdSenseIntegrationUpdate,
    session: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    integration = await _get_integration_for_user(session, current_user.id, integration_id)
    if integration.type != IntegrationType.ADSENSE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Integration type mismatch",
        )

    credentials = dict(integration.credentials)
    data = payload.dict(exclude_unset=True)

    if "account_id" in data and data["account_id"]:
        credentials["account_id"] = data["account_id"]
    if "access_token" in data and data["access_token"]:
        credentials["access_token"] = data["access_token"]
    if "refresh_token" in data and data["refresh_token"]:
        credentials["refresh_token"] = data["refresh_token"]
    if "client_id" in data and data["client_id"]:
        credentials["client_id"] = data["client_id"]
    if "client_secret" in data and data["client_secret"]:
        credentials["client_secret"] = data["client_secret"]

    expiry = None
    if data.get("token_expiry"):
        expiry = data["token_expiry"]
    elif "expires_in" in data:
        expiry = datetime.now(timezone.utc) + timedelta(seconds=data["expires_in"])

    if expiry is not None:
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        credentials["token_expiry"] = expiry.astimezone(timezone.utc).isoformat()

    integration.credentials = credentials
    await session.commit()
    await session.refresh(integration)
    return integration


@router.delete("/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_integration(
    integration_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    integration = await _get_integration_for_user(session, current_user.id, integration_id)
    await session.delete(integration)
    await session.commit()
