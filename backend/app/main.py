import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api import auth, integrations, metrics, users
from .core.config import get_settings
from .core.database import engine
from .models.base import Base
from .services.scheduler import shutdown_scheduler, start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    app.state.scheduler = None
    scheduler = await start_scheduler()
    app.state.scheduler = scheduler
    try:
        yield
    finally:
        await shutdown_scheduler(app.state.scheduler)


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, lifespan=lifespan)

    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(integrations.router)
    app.include_router(metrics.router)

    return app


app = create_app()
