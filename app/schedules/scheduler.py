import asyncio
import datetime
from typing import Callable

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore as JobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler as Scheduler
from celery.result import AsyncResult
from loguru import logger
from pydantic import BaseModel, field_validator

import app.worker.uipath as uipathtasks
from app.core.config import settings
from app.crud import uip_folder, uip_job
from app.db.session import DBContext

jobstore = JobStore(url=settings.SQLALCHEMY_DATABASE_URI)
scheduler = Scheduler(jobstores={"default": jobstore})


async def refresh_token() -> None:
    token = uipathtasks.FetchUIPathToken()
    uipathtasks.GetUIPathToken.apply_async()


async def refresh_folders() -> None:
    kwargs = {"fulldata": True, "upsert": True}
    uipathtasks.fetchfolders.apply_async(kwargs=kwargs)


async def refresh_sessions() -> None:
    kwargs = {"fulldata": True, "filter": None}
    uipathtasks.fetchsessions.apply_async(kwargs=kwargs)


async def refresh_processes_and_queues() -> None:
    folderlist = get_folderlist()
    kwargs = {"fulldata": True, "folderlist": folderlist, "filter": None}
    uipathtasks.fetchprocesses.apply_async(kwargs=kwargs)
    uipathtasks.fetchqueuedefinitions.apply_async(kwargs=kwargs)


async def refresh_queueitemevents() -> None:
    folderlist = get_folderlist()
    logger.info("Sending Queue Item Event Sync Request")
    kwargs = {
        "fulldata": True,
        "folderlist": folderlist,
        "filter": None,
        "synctimes": True,
    }
    uipathtasks.fetchqueueitemevents.apply_async(kwargs=kwargs)


async def refresh_queueitemnew() -> None:
    folderlist = get_folderlist()
    logger.info("Sending Queue Item New Sync Request")
    kwargs = {
        "fulldata": True,
        "folderlist": folderlist,
        "filter": None,
        "synctimes": True,
    }
    uipathtasks.fetchqueueitems.apply_async(kwargs=kwargs)


async def refresh_jobstarted() -> None:
    folderlist = get_folderlist()
    logger.info("Sending Jobs Started Sync Request")
    kwargs = {
        "fulldata": True,
        "folderlist": folderlist,
        "filter": None,
        "synctimes": True,
    }
    uipathtasks.fetchjobs.apply_async(kwargs=kwargs)


async def refresh_jobsunfinished() -> None:
    folderlist = get_folderlist()
    unfinished_ids = get_unfinishedjobs()
    if unfinished_ids:
        filter = f"Id in ({', '.join(str(x) for x in unfinished_ids)})"
        logger.info("Sending Poll Jobs Unfinished Request")
        kwargs = {
            "fulldata": True,
            "folderlist": folderlist,
            "filter": filter,
            "synctimes": False,
        }
        uipathtasks.fetchjobs.apply_async(kwargs=kwargs)


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


def get_unfinishedjobs() -> list[int] | None:
    # This one needs to be like this because it uses DBContext for APScheduler
    with DBContext() as db:
        jobids = uip_job.get_unfinished_jobid(db=db)
    return jobids


class Schedule(BaseModel):
    seconds: int = 15
    taskid: str
    taskfunction: Callable

    @field_validator("taskfunction")
    @classmethod
    def check_func(cls, v):
        if not callable(v):
            raise ValueError("taskfunction must be a callable")
        return v


# Main Schedules dict.
main_schedules = {
    "main_uip_token_refresh": Schedule(seconds=150, taskid="main_uip_token_refresh", taskfunction=refresh_token),
    "main_folder_refresh": Schedule(seconds=300, taskid="main_folder_refresh", taskfunction=refresh_folders),
    "main_sessions_refresh": Schedule(seconds=300, taskid="main_sessions_refresh", taskfunction=refresh_sessions),
    "main_processesandqueues_refresh": Schedule(
        seconds=300, taskid="main_processesandqueues_refresh", taskfunction=refresh_processes_and_queues
    ),
    "main_queueitemevent_refresh": Schedule(
        seconds=150, taskid="main_queueitemevent_refresh", taskfunction=refresh_queueitemevents
    ),
    "main_jobstarted_refresh": Schedule(seconds=150, taskid="main_jobstarted_refresh", taskfunction=refresh_jobstarted),
    "main_jobspolled_refresh": Schedule(
        seconds=150, taskid="main_jobspolled_refresh", taskfunction=refresh_jobsunfinished
    ),
}


def start_basic_schedules(schedules: dict[str, Schedule] = main_schedules):
    """Starts the schedules indicated in the argument

    Args:
        schedules (dict[str, Schedule], optional): _description_. Defaults to schedules.
    """
    logger.info("Adding Main Schedules...")
    for key, val in schedules.items():
        if not scheduler.get_job(val.taskid):
            logger.info(f"Adding task: {val.taskid}")
            scheduler.add_job(val.taskfunction, "interval", seconds=val.seconds, id=val.taskid, jobstore="default")
    logger.info("Main schedules checked")


scheduler.start(paused=True)
