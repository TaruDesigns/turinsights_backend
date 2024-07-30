# PENDING IMPLEMENTATION
"""
from app import schemas


def route_job(payload: schemas.JobPayload):
    job = payload.Job
    if payload.Type == "job.created":
        ...
        # Get Release Name From Key
        ReleaseName = ""
        obj = schemas.JobCreate(
            Key=job.Key,
            ReleaseName=job.Release.Name,
            CreationTime=payload.Timestamp,
            OrganizationUnitId=payload.OrganizationUnitId,
            Id=job.Id,
            State=job.State,
        )
        # CRUD
    elif payload.Type == "job.started":
        obj = schemas.JobUpdate
        ...
    elif payload.Type == "job.faulted":
        obj = schemas.JobUpdate
        ...
    elif payload.Type == "job.completed":
        obj = schemas.JobUpdate
        ...
    elif payload.Type == "job.stopped":
        obj = schemas.JobUpdate
        # Not supported
        ...
    elif payload.Type == "job.suspended":
        obj = schemas.JobUpdate
        ...
    else:
        ...
    ...


def route_queueitem(payload: schemas.QueueItemPayload):
    if payload.Type == "queueItem.added":
        schemas.QueueItemCreate
        ...
    elif payload.Type == "queueItem.transactionStarted":
        schemas.QueueItemUpdate
        ...
    elif payload.Type == "queueItem.transactionCompleted":
        schemas.QueueItemUpdate
        ...
    elif payload.Type == "queueItem.transactionFailed":
        schemas.QueueItemUpdate
        ...
    elif payload.Type == "queueItem.transactionAbandoned":
        schemas.QueueItemUpdate
        ...
        # not supported
    else:
        ...
    ...
"""
