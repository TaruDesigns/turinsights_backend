import asyncio
import datetime
from typing import Callable

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore as JobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler as Scheduler
from celery.result import AsyncResult
from loguru import logger
from pydantic import BaseModel, validator

from app.api.deps import DBContext
from app.core.celery_app import celery_app
from app.core.config import settings
from app.crud import uip_folder
from app.worker.uipath import FetchUIPathToken

jobstore = JobStore(url=settings.SQLALCHEMY_DATABASE_URI)
scheduler = Scheduler(jobstores={"default": jobstore})


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
    logger.info("Sending Queue Item Event Sync Request")
    kwargs = {
        "fulldata": True,
        "folderlist": folderlist,
        "filter": None,
        "synctimes": True,
    }
    celery_app.send_task("app.worker.uipath.fetchqueueitemevents", kwargs=kwargs)


async def refresh_queueitemnew() -> None:
    folderlist = get_folderlist()
    logger.info("Sending Queue Item New Sync Request")
    kwargs = {
        "fulldata": True,
        "folderlist": folderlist,
        "filter": None,
        "synctimes": True,
    }
    celery_app.send_task("app.worker.uipath.fetchqueueitems", kwargs=kwargs)


async def refresh_jobstarted() -> None:
    folderlist = get_folderlist()
    logger.info("Sending Jobs Started Sync Request")
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


class Schedule(BaseModel):
    seconds: int = 15
    taskid: str
    taskfunction: Callable

    @validator("taskfunction")
    def check_func(cls, v):
        if not callable(v):
            raise ValueError("taskfunction must be a callable")
        return v


# Main Schedules dict.
schedules = {
    "main_uip_token_refresh": Schedule(seconds=150, taskid="main_uip_token_refresh", taskfunction=refresh_token),
    "main_folder_refresh": Schedule(seconds=30, taskid="main_folder_refresh", taskfunction=refresh_folders),
    "main_sessions_refresh": Schedule(seconds=30, taskid="main_sessions_refresh", taskfunction=refresh_sessions),
    "main_processesandqueues_refresh": Schedule(
        seconds=30, taskid="main_processesandqueues_refresh", taskfunction=refresh_processes_and_queues
    ),
    "main_queueitemevent_refresh": Schedule(
        seconds=15, taskid="main_queueitemevent_refresh", taskfunction=refresh_queueitemevents
    ),
    "main_jobstarted_refresh": Schedule(seconds=15, taskid="main_jobstarted_refresh", taskfunction=refresh_jobstarted),
}


def start_basic_schedules(schedules: dict[str, Schedule] = schedules):
    """Starts the schedules indicated in the argument

    Args:
        schedules (dict[str, Schedule], optional): _description_. Defaults to schedules.
    """
    logger.info("Adding Main Schedules...")
    for key, val in schedules.items():
        if not scheduler.get_job(val.taskid):
            logger.info(f"Adding task: {val.taskid}")
            scheduler.add_job(val.taskfunction, "interval", seconds=val.seconds, id=val.taskid)
    logger.info("Main schedules checked")
