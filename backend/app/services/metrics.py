from __future__ import annotations

from datetime import date
from typing import Dict, Iterable, Optional

import asyncio
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.integration import IntegrationAccount, IntegrationType
from ..models.metrics import DailyMetric
from ..models.user import User
from .facebook import FacebookAdsClient
from .google_adsense import GoogleAdSenseClient


async def get_user(session: AsyncSession, user_id: int) -> Optional[User]:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


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
        client = GoogleAdSenseClient(
            account_id=credentials["account_id"],
            access_token=credentials["access_token"],
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
