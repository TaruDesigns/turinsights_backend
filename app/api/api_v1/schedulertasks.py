from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger
from uipath_orchestrator_rest.rest import ApiException

import app.worker.uipath as uipathtasks
from app import crud, schemas
from app.api import deps
from app.schedules import scheduler as schmodule


class JobSchema(schemas.BaseSchema):
    id: str
    name: str
    interval: float
    nextrun: Optional[datetime]


router = APIRouter()


@router.post("/resume", response_model=None, status_code=201)
def resumescheduler(scheduler=Depends(deps.get_scheduler)):
    # Resume scheduler
    scheduler.resume()


@router.post("/pause", response_model=None, status_code=201)
def pausescheduler(scheduler=Depends(deps.get_scheduler)):
    # Resume scheduler
    scheduler.pause()


@router.post("/reinit", response_model=None, status_code=201)
def reinit(scheduler=Depends(deps.get_scheduler)):
    # Reinit scheduler with default main jobs
    scheduler.shutdown()
    schmodule.start_basic_schedules()
    scheduler.start()


@router.get("/schedules", response_model=None, status_code=200)
def getschedules(scheduler=Depends(deps.get_scheduler)) -> list[JobSchema]:
    # Get all jobs currently added to scheduler
    alljobs = scheduler.get_jobs()
    alljobschemas = [
        JobSchema(id=job.id, name=job.name, interval=job.trigger.interval_length, nextrun=job.next_run_time)
        for job in alljobs
    ]
    return alljobschemas


@router.get("/schedule/{id}", response_model=None, status_code=200)
def getschedulebyid(id: str, scheduler=Depends(deps.get_scheduler)) -> JobSchema | None:
    # Get schedule based on id in the path and update its interval (in seconds)
    job = scheduler.get_job(id)
    if job is None:
        raise HTTPException(status_code=404, detail="Invalid ID, job doesn't exist")
    return JobSchema(id=job.id, name=job.name, interval=job.trigger.interval_length, nextrun=job.next_run_time)


@router.patch("/schedule/{id}", response_model=None, status_code=201)
def updateschedule(id: str, interval: float, scheduler=Depends(deps.get_scheduler)) -> None:
    # Get schedule based on id in the path and update its interval (in seconds)
    job = scheduler.get_job(id)
    if job is None:
        raise HTTPException(status_code=404, detail="Invalid ID, job doesn't exist")
    scheduler.reschedule_job(id=id, trigger="interval", seconds=interval)


"""
@router.post("/schedule", response_model=None, status_code=201)
def postschedule(id: str, interval: float, scheduler=Depends(deps.get_scheduler())) -> None:
    # Get schedule based on id in the path and update its interval (in seconds)
    job = scheduler.get_job(id=id)
    if job is None:
        raise ValueError("Invalid ID, job doesn't exist")
    scheduler.reschedule_job(id=id, trigger='interval', seconds=interval)
"""
