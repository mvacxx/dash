from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Dict, Iterable, Optional

import asyncio
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.integration import IntegrationAccount, IntegrationType
from ..models.metrics import DailyMetric
from .facebook import FacebookAdsClient
from .google_adsense import GoogleAdSenseClient


async def get_integrations(
    session: AsyncSession, user_id: int, integration_type: Optional[IntegrationType] = None
) -> Iterable[IntegrationAccount]:
    query = select(IntegrationAccount).where(IntegrationAccount.user_id == user_id)
    if integration_type is not None:
        query = query.where(IntegrationAccount.type == integration_type)
    result = await session.execute(query)
    return result.scalars().all()


def calculate_roi(spend: float, revenue: float) -> float:
    if spend == 0:
        return 0.0
    return (revenue - spend) / spend


async def upsert_metric(
    session: AsyncSession,
    user_id: int,
    metric_day: date,
    spend: float,
    revenue: float,
) -> DailyMetric:
    roi = calculate_roi(spend, revenue)

    query = select(DailyMetric).where(
        and_(DailyMetric.user_id == user_id, DailyMetric.metric_date == metric_day)
    )
    result = await session.execute(query)
    instance = result.scalar_one_or_none()

    if instance is None:
        instance = DailyMetric(
            user_id=user_id,
            metric_date=metric_day,
            spend=spend,
            revenue=revenue,
            roi=roi,
        )
        session.add(instance)
    else:
        instance.spend = spend
        instance.revenue = revenue
        instance.roi = roi

    await session.flush()
    return instance


async def _ensure_adsense_access_token(
    session: AsyncSession, integration: IntegrationAccount
) -> str:
    credentials = dict(integration.credentials)
    now = datetime.now(timezone.utc)
    should_refresh = True

    token_expiry_raw = credentials.get("token_expiry")
    if token_expiry_raw:
        try:
            expiry = datetime.fromisoformat(token_expiry_raw)
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=timezone.utc)
            should_refresh = expiry <= now + timedelta(minutes=5)
        except ValueError:
            should_refresh = True
    else:
        should_refresh = True

    if should_refresh:
        refreshed = await asyncio.to_thread(
            GoogleAdSenseClient.refresh_access_token,
            client_id=credentials["client_id"],
            client_secret=credentials["client_secret"],
            refresh_token=credentials["refresh_token"],
        )
        credentials["access_token"] = refreshed["access_token"]
        credentials["token_expiry"] = refreshed["token_expiry"]
        integration.credentials = credentials
        await session.flush()

    return credentials["access_token"]


async def sync_daily_metrics(session: AsyncSession, user_id: int, metric_day: date) -> DailyMetric:
    facebook_integrations = await get_integrations(session, user_id, IntegrationType.FACEBOOK)
    adsense_integrations = await get_integrations(session, user_id, IntegrationType.ADSENSE)

    total_spend = 0.0
    total_revenue = 0.0

    for integration in facebook_integrations:
        credentials = integration.credentials
        client = FacebookAdsClient(
            access_token=credentials["access_token"],
            account_id=credentials["account_id"],
            api_version=credentials.get("api_version", "v18.0"),
            business_id=credentials.get("business_id"),
        )
        metrics = await asyncio.to_thread(client.fetch_daily_metrics, metric_day)
        total_spend += metrics.get("spend", 0.0)
        total_revenue += metrics.get("revenue", 0.0)

    for integration in adsense_integrations:
        credentials = integration.credentials
        access_token = credentials.get("access_token")
        if not access_token:
            access_token = await _ensure_adsense_access_token(session, integration)
        else:
            now = datetime.now(timezone.utc)
            expiry_raw = credentials.get("token_expiry")
            if expiry_raw:
                try:
                    expiry = datetime.fromisoformat(expiry_raw)
                    if expiry.tzinfo is None:
                        expiry = expiry.replace(tzinfo=timezone.utc)
                    if expiry <= now + timedelta(minutes=5):
                        access_token = await _ensure_adsense_access_token(session, integration)
                except ValueError:
                    access_token = await _ensure_adsense_access_token(session, integration)
            else:
                access_token = await _ensure_adsense_access_token(session, integration)

        client = GoogleAdSenseClient(
            account_id=credentials["account_id"],
            access_token=access_token,
        )

        try:
            earnings = await asyncio.to_thread(client.fetch_daily_earnings, metric_day)
        except GoogleAdSenseClient.UnauthorizedError:
            access_token = await _ensure_adsense_access_token(session, integration)
            client = GoogleAdSenseClient(
                account_id=credentials["account_id"],
                access_token=access_token,
            )
            earnings = await asyncio.to_thread(client.fetch_daily_earnings, metric_day)

        total_revenue += earnings

    metric = await upsert_metric(
        session=session,
        user_id=user_id,
        metric_day=metric_day,
        spend=total_spend,
        revenue=total_revenue,
    )
    await session.commit()
    return metric


async def list_metrics(
    session: AsyncSession, user_id: int, start: date, end: date
) -> Dict[str, float]:
    query = (
        select(DailyMetric)
        .where(
            and_(
                DailyMetric.user_id == user_id,
                DailyMetric.metric_date >= start,
                DailyMetric.metric_date <= end,
            )
        )
        .order_by(DailyMetric.metric_date)
    )
    result = await session.execute(query)
    metrics = result.scalars().all()

    total_spend = sum(metric.spend for metric in metrics)
    total_revenue = sum(metric.revenue for metric in metrics)
    average_roi = sum(metric.roi for metric in metrics) / len(metrics) if metrics else 0.0

    return {
        "metrics": metrics,
        "total_spend": total_spend,
        "total_revenue": total_revenue,
        "average_roi": average_roi,
    }
