import asyncio

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import settings
from app.database.session import SessionLocal
from app.services.sre_service import run_all_checks


def scheduled_check():
    async def _run():
        db = SessionLocal()
        try:
            await run_all_checks(db)
        finally:
            db.close()

    asyncio.run(_run())


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        scheduled_check,
        trigger="interval",
        seconds=settings.monitor_interval_seconds,
        id="sre-health-monitor",
        replace_existing=True,
    )
    scheduler.start()
    return scheduler


def stop_scheduler(scheduler):
    if scheduler and scheduler.running:
        scheduler.shutdown(wait=False)
