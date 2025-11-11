from datetime import date

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select

from ..core.config import get_settings
from ..core.database import AsyncSessionLocal
from ..models.user import User
from .metrics import sync_daily_metrics


async def _sync_all_users() -> None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User.id))
        user_ids = [row[0] for row in result.all()]
        today = date.today()
        for user_id in user_ids:
            await sync_daily_metrics(session, user_id, today)


async def start_scheduler() -> AsyncIOScheduler:
    settings = get_settings()
    scheduler = AsyncIOScheduler(timezone="UTC")
    trigger = CronTrigger(
        hour=settings.scheduler_daily_hour_utc,
        minute=settings.scheduler_daily_minute_utc,
    )
    scheduler.add_job(_sync_all_users, trigger, id="daily-sync", replace_existing=True)
    scheduler.start()
    return scheduler


async def shutdown_scheduler(scheduler: AsyncIOScheduler | None) -> None:
    if scheduler is not None:
        await scheduler.shutdown(wait=False)
