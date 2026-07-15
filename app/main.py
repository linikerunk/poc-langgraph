from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import admin, mock_api, sre
from app.core.config import settings
from app.database.base import Base
from app.database.session import engine
from app.monitoring.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    scheduler = start_scheduler()
    yield
    stop_scheduler(scheduler)


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(mock_api.router)
app.include_router(admin.router)
app.include_router(sre.router)


@app.get("/")
def root():
    return {
        "name": settings.app_name,
        "docs": "/docs",
        "health": "/api/health",
    }
