import asyncio
import datetime
import logging

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore as JobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler as Scheduler
from celery.result import AsyncResult

from app.api.deps import DBContext, get_db
from app.core.celery_app import celery_app
from app.core.config import settings
from app.crud import tracked_synctimes, uip_folder
from app.worker.uipath import FetchUIPathToken

jobstore = JobStore(url=settings.SQLALCHEMY_DATABASE_URI)
scheduler = Scheduler(jobstores={"default": jobstore})


def start_basic_schedules():
    logging.info("Adding Basic Schedules...")
    if not scheduler.get_job("main_uip_token_refresh"):
        scheduler.add_job(
            refresh_token, "interval", seconds=150, id="main_uip_token_refresh"
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
            seconds=30,
            id="main_sessions_refresh",
        )
    if not scheduler.get_job("main_processesandqueues_refresh"):
        scheduler.add_job(
            refresh_processes_and_queues,
            "interval",
            seconds=30,
            id="main_processesandqueues_refresh",
        )
    if not scheduler.get_job("main_queueitemevent_refresh"):
        scheduler.add_job(
            refresh_queueitemevents,
            "interval",
            seconds=10,
            id="main_queueitemevent_refresh",
        )
    if not scheduler.get_job("main_queueitemnew_refresh"):
        scheduler.add_job(
            refresh_queueitemnew,
            "interval",
            seconds=20,
            id="main_queueitemnew_refresh",
        )
    if not scheduler.get_job("main_jobstarted_refresh"):
        scheduler.add_job(
            refresh_jobstarted,
            "interval",
            seconds=15,
            id="main_jobstarted_refresh",
        )


async def refresh_token() -> None:
    token = FetchUIPathToken()
    celerytoken = celery_app.send_task("app.worker.uipath.GetUIPathToken")


async def refresh_folders() -> None:
    kwargs = {"fulldata": True, "upsert": True}
    celery_app.send_task("app.worker.uipath.fetchfolders", kwargs=kwargs)


async def refresh_sessions() -> None:
    kwargs = {"fulldata": True, "filter": None}
    celery_app.send_task("app.worker.uipath.fetchsessions", kwargs=kwargs)


async def refresh_processes_and_queues() -> None:
    folderlist = get_folderlist()
    kwargs = {"fulldata": True, "folderlist": folderlist, "filter": None}
    celery_app.send_task("app.worker.uipath.fetchprocesses", kwargs=kwargs)
    celery_app.send_task("app.worker.uipath.fetchqueuedefinitions", kwargs=kwargs)


async def refresh_queueitemevents() -> None:
    # todo CHANGE THIS AND MAKE IT WORK WITH ASYNC
    folderlist = get_folderlist()
    logging.info("Sending Queue Item Event Sync Request")
    kwargs = {
        "fulldata": True,
        "folderlist": folderlist,
        "filter": None,
        "synctimes": True,
    }
    celery_app.send_task("app.worker.uipath.fetchqueueitemevents", kwargs=kwargs)


async def refresh_queueitemnew() -> None:
    folderlist = get_folderlist()
    logging.info("Sending Queue Item New Sync Request")
    kwargs = {
        "fulldata": True,
        "folderlist": folderlist,
        "filter": None,
        "synctimes": True,
    }
    celery_app.send_task("app.worker.uipath.fetchqueueitems", kwargs=kwargs)


async def refresh_jobstarted() -> None:
    folderlist = get_folderlist()
    logging.info("Sending Jobs Started Sync Request")
    kwargs = {
        "fulldata": True,
        "folderlist": folderlist,
        "filter": None,
        "synctimes": True,
    }
    celery_app.send_task("app.worker.uipath.fetchjobs", kwargs=kwargs)


async def wait_for_result(result: AsyncResult, timeout: int = 30):
    # Use asyncio.to_thread to run the blocking result.ready() in a separate thread
    start_time = datetime.datetime.now()
    while not result.ready():
        await asyncio.sleep(1)  # Yield control to the event loop for 1 second
        if (datetime.datetime.now() - start_time).seconds > timeout:
            return False
    return result.successful()


def get_folderlist() -> list:
    # This one needs to be like this because it uses DBContext for APScheduler
    with DBContext() as db:
        folderlist = uip_folder.get_multi(db=db)
        folderlist = [folder.Id for folder in folderlist]
    return folderlist
