from datetime import date, datetime
from typing import List
from pydantic import BaseModel


class DailyMetricRead(BaseModel):
    id: int
    metric_date: date
    spend: float
    revenue: float
    roi: float
    created_at: datetime

    class Config:
        orm_mode = True


class MetricsSummary(BaseModel):
    metric_date: date
    spend: float
    revenue: float
    roi: float


class MetricsResponse(BaseModel):
    metrics: List[MetricsSummary]
    total_spend: float
    total_revenue: float
    average_roi: float
