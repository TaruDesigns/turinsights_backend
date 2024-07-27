import logging
import datetime

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore as JobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler as Scheduler

from app.api.deps import get_db, DBContext
from app.core.celery_app import celery_app
from app.core.config import settings
from app.crud import uip_folder, tracked_synctimes
from app.worker.uipath import FetchUIPathToken

jobstore = JobStore(url=settings.SQLALCHEMY_DATABASE_URI)
scheduler = Scheduler(jobstores={"default": jobstore})


def start_basic_schedules():
    logging.info("Adding Basic Schedules...")
    if not scheduler.get_job("main_uip_token_refresh"):
        scheduler.add_job(
            refresh_token, "interval", seconds=150, id="main_uip_token_refresh"
        )
    if not scheduler.get_job("main_queueitemevent_refresh"):
        scheduler.add_job(
            refresh_queueitemevents,
            "interval",
            seconds=15,
            id="main_queueitemevent_refresh",
        )
    if not scheduler.get_job("main_folder_refresh"):
        scheduler.add_job(
            refresh_folders,
            "interval",
            seconds=30,
            id="main_folder_refresh",
        )
    if not scheduler.get_job("main_sessions_refresh"):
        scheduler.add_job(
            refresh_sessions,
            "interval",
            seconds=10,
            id="main_sessions_refresh",
        )


async def refresh_token() -> None:
    token = FetchUIPathToken()
    celerytoken = celery_app.send_task("app.worker.uipath.GetUIPathToken")


async def refresh_folders() -> None:
    kwargs = {"fulldata": True, "upsert": True}
    celery_app.send_task("app.worker.uipath.fetchfolders", kwargs=kwargs)


async def refresh_jobs() -> None:
    folderlist = get_folderlist()
    kwargs = {"fulldata": True, "folderlist": folderlist, "filter": None}
    celery_app.send_task("app.worker.uipath.fetchjobs", kwargs=kwargs)


async def refresh_sessions() -> None:
    kwargs = {"fulldata": True, "filter": None}
    celery_app.send_task("app.worker.uipath.fetchsessions", kwargs=kwargs)


async def refresh_transactions() -> None:
    folderlist = get_folderlist()
    kwargs = {"fulldata": True, "folderlist": folderlist, "filter": None}
    celery_app.send_task("app.worker.uipath.fetchqueueitemevents", kwargs=kwargs)
    celery_app.send_task("app.worker.uipath.fetchqueueitems", kwargs=kwargs)


async def refresh_processes_and_queues() -> None:
    folderlist = get_folderlist()
    kwargs = {"fulldata": True, "folderlist": folderlist, "filter": None}
    celery_app.send_task("app.worker.uipath.fetchprocesses", kwargs=kwargs)
    celery_app.send_task("app.worker.uipath.fetchqueuedefinitions", kwargs=kwargs)


async def refresh_queueitemevents() -> None:
    folderlist = get_folderlist()
    with DBContext() as db:
        lastsynctime = tracked_synctimes.get_queueitemevent(db=db)
    filter = (
        f"Timestamp gt {lastsynctime.isoformat()}Z" if lastsynctime else None
    )  # Filter will be retrieved as 'gt than last sync time'
    logging.info(f"Sending Queue Item Event Sync Request: '{filter}'")
    kwargs = {"fulldata": True, "folderlist": folderlist, "filter": filter}
    task_sync_time = datetime.datetime.now()
    result = celery_app.send_task(
        "app.worker.uipath.fetchqueueitemevents", kwargs=kwargs
    )
    result.wait(timeout=30)
    if result.ready() and result.successful():
        with DBContext() as db:
            tracked_synctimes.update_queueitemevent(db=db, newtime=task_sync_time)
        logging.info(f" Queue Item Event Succesfully synced: '{filter}'")
    else:
        logging.info(f" Queue Item Event Not synced: '{filter}'")


def get_folderlist() -> list:
    with DBContext() as db:
        folderlist = uip_folder.get_multi(db=db)
        folderlist = [folder.Id for folder in folderlist]
    return folderlist
