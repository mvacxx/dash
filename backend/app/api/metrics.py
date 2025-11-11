from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.metrics import MetricsResponse
from ..services.metrics import list_metrics, sync_daily_metrics
from .deps import get_current_user, get_db_session

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.post("/sync")
async def sync_metrics(
    metric_date: date = Query(..., alias="date"),
    session: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    metric = await sync_daily_metrics(session, current_user.id, metric_date)
    return {
        "id": metric.id,
        "metric_date": metric.metric_date,
        "spend": metric.spend,
        "revenue": metric.revenue,
        "roi": metric.roi,
    }


@router.get("", response_model=MetricsResponse)
async def get_metrics(
    start_date: date,
    end_date: date,
    session: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    data = await list_metrics(session, current_user.id, start_date, end_date)
    return {
        "metrics": [
            {
                "metric_date": metric.metric_date,
                "spend": metric.spend,
                "revenue": metric.revenue,
                "roi": metric.roi,
            }
            for metric in data["metrics"]
        ],
        "total_spend": data["total_spend"],
        "total_revenue": data["total_revenue"],
        "average_roi": data["average_roi"],
    }
