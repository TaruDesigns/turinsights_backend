import logging
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uipath_orchestrator_rest.rest import ApiException

import app.worker.uipath
from app import crud, schemas
from app.api import deps
from app.core.celery_app import celery_app
from app.worker.uipath import FetchUIPathToken, GetUIPathToken

router = APIRouter()


# -------------------------------
# -------------Folders----------
# -------------------------------
@router.post("/folders", response_model=None, status_code=201)
def fetchfolders(
    formdata: schemas.UIPFetchPostBody,
) -> Any:
    """Get folders and save in DB (optional). Set formdata.cruddb to True

    Args:
        db (Session, optional): Database session. Defaults to Depends(deps.get_db).
        formdata (UIPFetchPostBody): Form Data (JSON Body)

    Returns:
        folderlist: List of Folders (Pydantic models)
    """
    try:
        # Gets folders.
        kwargs = {"fulldata": formdata.fulldata, "upsert": formdata.upsert}
        celery_app.send_task("app.worker.uipath.fetchfolders", kwargs=kwargs)
    except ApiException as e:
        logging.error(f"Exception when calling FoldersApi->folders_get: {e.body}")
        raise HTTPException(
            status_code=409, detail=f"Could not request data to UIPath: {e.body}"
        )
    except Exception as e:
        logging.error(f"Error when updating database: Folders: {e}")
        raise HTTPException(
            status_code=409, detail="Could not update database: Folders"
        )
    return {"msg": "Request accepted"}


@router.get("/folders", response_model=None, status_code=201)
def getfolders(
    filter: Optional[str] = Query(None),
    select: Optional[str] = Query(None),
    top: Optional[int] = Query(100),
    skip: Optional[int] = Query(0),
    db: Session = Depends(deps.get_db),
) -> Any:
    """Get folders from DB

    Args:
        db (Session, optional): Database session. Defaults to Depends(deps.get_db).
        Standard OData Queries

    Returns:
        results: List of Folders (Pydantic models)
    """
    if filter:
        try:
            return crud.uip_folder.get_odata(db=db, filter=filter)
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid OData Query")
    else:
        try:
            return crud.uip_folder.get_multi(db=db, skip=skip, limit=top)
        except Exception as e:
            raise HTTPException(status_code=503, detail="Error retrieving data")


# -------------------------------
# ---------------Jobs------------
# -------------------------------
@router.post("/jobs", response_model=None, status_code=201)
def fetchjobs(formdata: schemas.UIPFetchPostBody) -> Any:
    """Get Jobs and save in DB (optional). Set formdata.cruddb to True

    Args:
        db (Session, optional): Database session. Defaults to Depends(deps.get_db).
        formdata (UIPFetchPostBody): Form Data (JSON Body)

    Returns:
        results: List of Jobs (Pydantic models)
    """
    if formdata.filter:
        filter = formdata.filter
    else:
        filter = None
    try:
        kwargs = {
            "fulldata": formdata.fulldata,
            "upsert": formdata.upsert,
            "filter": filter,
            "folderlist": formdata.folderlist,
        }
        celery_app.send_task("app.worker.uipath.fetchjobs", kwargs=kwargs)
    except ApiException as e:
        logging.error(f"Exception when calling JobsAPI->jobs_get: {e.body}")
        raise HTTPException(
            status_code=409, detail=f"Could not request data to UIPath: {e.body}"
        )
    except Exception as e:
        logging.error(f"Error when updating database: Jobs: {e}")
        raise HTTPException(status_code=409, detail="Could not update database: Jobs.")
    return {"msg": "Request accepted"}


@router.get("/jobs", response_model=None, status_code=201)
def getjobs(
    filter: Optional[str] = Query(None),
    select: Optional[str] = Query(None),
    top: Optional[int] = Query(100),
    skip: Optional[int] = Query(0),
    db: Session = Depends(deps.get_db),
) -> Any:
    """Get folders from DB

    Args:
        db (Session, optional): Database session. Defaults to Depends(deps.get_db).
        Standard OData Queries

    Returns:
        results: List of Jobs (Pydantic models)
    """
    if filter:
        try:
            return crud.uip_job.get_odata(db=db, filter=filter)
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid OData Query")
    else:
        try:
            return crud.uip_job.get_multi(db=db, skip=skip, limit=top)
        except Exception as e:
            raise HTTPException(status_code=503, detail="Error retrieving data")


# -------------------------------
# ------------Processes---------
# -------------------------------
@router.post("/processes", response_model=None, status_code=201)
def fetchprocesses(formdata: schemas.UIPFetchPostBody) -> Any:
    """Get Processes and save in DB (optional). Set formdata.cruddb to True

    Args:
        db (Session, optional): Database session. Defaults to Depends(deps.get_db).
        formdata (UIPFetchPostBody): Form Data (JSON Body)

    Returns:
        results: List of Processes (Pydantic models)
    """
    if formdata.filter:
        filter = formdata.filter
    else:
        filter = None
    try:
        kwargs = {
            "fulldata": formdata.fulldata,
            "upsert": formdata.upsert,
            "filter": filter,
            "folderlist": formdata.folderlist,
        }
        celery_app.send_task("app.worker.uipath.fetchprocesses", kwargs=kwargs)
    except ApiException as e:
        logging.error(f"Exception when calling ReleasesAPI->releases_get: {e.body}")
        raise HTTPException(
            status_code=409, detail=f"Could not request data to UIPath: {e.body}"
        )
    except Exception as e:
        logging.error(f"Error when updating database: Processes: {e}")
        raise HTTPException(
            status_code=409, detail="Could not update database: Processes"
        )
    return {"msg": "Request accepted"}


@router.get("/processes", response_model=None, status_code=201)
def getprocesses(
    filter: Optional[str] = Query(None),
    select: Optional[str] = Query(None),
    top: Optional[int] = Query(100),
    skip: Optional[int] = Query(0),
    db: Session = Depends(deps.get_db),
) -> Any:
    """Get Processes from DB

    Args:
        db (Session, optional): Database session. Defaults to Depends(deps.get_db).
        Standard OData Queries

    Returns:
        results: List of Processes (Pydantic models)
    """
    if filter:
        try:
            return crud.uip_process.get_odata(db=db, filter=filter)
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid OData Query")
    else:
        try:
            return crud.uip_process.get_multi(db=db, skip=skip, limit=top)
        except Exception as e:
            raise HTTPException(status_code=503, detail="Error retrieving data")


# -------------------------------
# ----------QueueDefinitions---
# -------------------------------
@router.post("/queuedefinitions", response_model=None, status_code=201)
def fetchqueuedefinitions(formdata: schemas.UIPFetchPostBody) -> Any:
    """Get Queue Definitions and save in DB (optional). Set formdata.cruddb to True

    Args:
        db (Session, optional): Database session. Defaults to Depends(deps.get_db).
        formdata (UIPFetchPostBody): Form Data (JSON Body)

    Returns:
        results: List of QueueDefinitions (Pydantic models)
    """
    if formdata.filter:
        filter = formdata.filter
    else:
        filter = None
    try:
        kwargs = {
            "fulldata": formdata.fulldata,
            "upsert": formdata.upsert,
            "filter": filter,
            "folderlist": formdata.folderlist,
        }
        celery_app.send_task("app.worker.uipath.fetchqueuedefinitions", kwargs=kwargs)
    except ApiException as e:
        logging.error(
            f"Exception when calling QueueDefinitionsAPI->queuedefinitions_get {e.body}"
        )
        raise HTTPException(
            status_code=409, detail=f"Could not request data to UIPath: {e.body}"
        )
    except Exception as e:
        logging.error(f"Error when updating database: Processes: {e}")
        raise HTTPException(
            status_code=409, detail="Could not update database: QueueDefinitions"
        )
    return {"msg": "Request accepted"}


@router.get("/queuedefinitions", response_model=None, status_code=201)
def getqueuedefinitions(
    filter: Optional[str] = Query(None),
    select: Optional[str] = Query(None),
    top: Optional[int] = Query(100),
    skip: Optional[int] = Query(0),
    db: Session = Depends(deps.get_db),
) -> Any:
    """Get queuedefinitions from DB

    Args:
        db (Session, optional): Database session. Defaults to Depends(deps.get_db).
        Standard OData Queries

    Returns:
        results: List of QueueDefinitions (Pydantic models)
    """
    if filter:
        try:
            return crud.uip_queue_definitions.get_odata(db=db, filter=filter)
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid OData Query")
    else:
        try:
            return crud.uip_queue_definitions.get_multi(db=db, skip=skip, limit=top)
        except Exception as e:
            raise HTTPException(status_code=503, detail="Error retrieving data")


# -------------------------------
# -------QueueItems--------------
# -------------------------------
@router.post("/queueitems", response_model=None, status_code=201)
def fetchqueueitems(formdata: schemas.UIPFetchPostBody) -> Any:
    """Get QueueItems and save in DB (optional). Set formdata.cruddb to True

    Args:
        db (Session, optional): Database session. Defaults to Depends(deps.get_db).
        formdata (UIPFetchPostBody): Form Data (JSON Body)

    Returns:
        results: List of QueueItems (Pydantic models)
    """
    if formdata.filter:
        filter = formdata.filter
    else:
        filter = None
    try:
        kwargs = {
            "fulldata": formdata.fulldata,
            "upsert": formdata.upsert,
            "filter": filter,
            "folderlist": formdata.folderlist,
        }
        celery_app.send_task("app.worker.uipath.fetchqueueitems", kwargs=kwargs)
    except ApiException as e:
        logging.error(f"Exception when calling QueueItemsAPI->queueItems_get:{e.body}")
        raise HTTPException(
            status_code=409, detail=f"Could not request data to UIPath: {e.body}"
        )
    except Exception as e:
        logging.error(f"Error when updating database: QueueItems: {e}")
        raise HTTPException(
            status_code=409, detail="Could not update database: QueueItems"
        )
    return {"msg": "Request accepted"}


@router.get("/queueitems", response_model=None, status_code=201)
def getqueueitems(
    filter: Optional[str] = Query(None),
    select: Optional[str] = Query(None),
    top: Optional[int] = Query(100),
    skip: Optional[int] = Query(0),
    db: Session = Depends(deps.get_db),
) -> Any:
    """Get folders from DB

    Args:
        db (Session, optional): Database session. Defaults to Depends(deps.get_db).
        Standard OData Queries

    Returns:
        results: List of QueueItems (Pydantic models)
    """
    if filter:
        try:
            return crud.uip_queue_item.get_odata(db=db, filter=filter)
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid OData Query")
    else:
        try:
            return crud.uip_queue_item.get_multi(db=db, skip=skip, limit=top)
        except Exception as e:
            raise HTTPException(status_code=503, detail="Error retrieving data")


# -------------------------------
# -------QueueItemEvents-----------
# -------------------------------
@router.post("/queueitemevents", response_model=None, status_code=201)
def fetchqueueitemevents(formdata: schemas.UIPFetchPostBody) -> Any:
    """Get Queue Item Events and save in DB (optional). Set formdata.cruddb to True

    Args:
        db (Session, optional): Database session. Defaults to Depends(deps.get_db).
        formdata (UIPFetchPostBody): Form Data (JSON Body)

    Returns:
        results: List of QueueItemEvents (Pydantic models)
    """
    if formdata.filter:
        filter = formdata.filter
    else:
        filter = None
    try:
        kwargs = {
            "fulldata": formdata.fulldata,
            "upsert": formdata.upsert,
            "filter": filter,
            "folderlist": formdata.folderlist,
        }
        celery_app.send_task("app.worker.uipath.fetchqueueitemevents", kwargs=kwargs)
    except ApiException as e:
        logging.error(f"Exception when calling QueueItemsAPI->queueItems_get: {e.body}")
        raise HTTPException(
            status_code=409, detail=f"Could not request data to UIPath: {e.body}"
        )
    except Exception as e:
        logging.error(f"Error when updating database: QueueItemEvents: {e}")
        raise HTTPException(
            status_code=409, detail="Could not update database: QueueItemEvents"
        )
    return {"msg": "Request accepted"}


@router.get("/queueitemevents", response_model=None, status_code=201)
def getqueueitemevents(
    filter: Optional[str] = Query(None),
    select: Optional[str] = Query(None),
    top: Optional[int] = Query(100),
    skip: Optional[int] = Query(0),
    db: Session = Depends(deps.get_db),
) -> Any:
    """Get queueitemevents from DB

    Args:
        db (Session, optional): Database session. Defaults to Depends(deps.get_db).
        Standard OData Queries
    Returns:
        results: List of QueueItemEvents (Pydantic models)
    """
    if filter:
        try:
            return crud.uip_queue_item_event.get_odata(db=db, filter=filter)
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid OData Query")
    else:
        try:
            return crud.uip_queue_item_event.get_multi(db=db, skip=skip, limit=top)
        except Exception as e:
            raise HTTPException(status_code=503, detail="Error retrieving data")


# -------------------
# -----------Sessions
# --------------------
@router.post("/sessions", response_model=None, status_code=201)
def fetchsessions(formdata: schemas.UIPFetchPostBody) -> Any:
    """Get sessions and save in DB (optional). Set formdata.cruddb to True

    Args:
        db (Session, optional): Database session. Defaults to Depends(deps.get_db).
        formdata (UIPFetchPostBody): Form Data (JSON Body)

    Returns:
        sessions: List of sessions (Pydantic models)
    """
    if formdata.filter:
        filter = formdata.filter
    else:
        filter = None
    try:
        kwargs = {
            "fulldata": formdata.fulldata,
            "upsert": formdata.upsert,
            "filter": filter,
            "folderlist": formdata.folderlist,
        }
        celery_app.send_task("app.worker.uipath.fetchsessions", kwargs=kwargs)
    except ApiException as e:
        logging.error(f"Exception when calling SessionsAPI->sessions_get {e.body}")
        raise HTTPException(
            status_code=409, detail=f"Could not request data to UIPath: {e.body}"
        )
    except Exception as e:
        logging.error(f"Error when updating database: Sessions: {e}")
        raise HTTPException(
            status_code=409, detail="Could not update database: Sessions"
        )
    return {"msg": "Request accepted"}


@router.get("/sessions", response_model=None, status_code=201)
def getsessions(
    filter: Optional[str] = Query(None),
    select: Optional[str] = Query(None),
    top: Optional[int] = Query(100),
    skip: Optional[int] = Query(0),
    db: Session = Depends(deps.get_db),
) -> Any:
    """Get Sessions from DB

    Args:
        db (Session, optional): Database session. Defaults to Depends(deps.get_db).
        OData Queries

    Returns:
       sessions: List of sessions (Pydantic models)
    """
    if filter:
        try:
            return crud.uip_session.get_odata(db=db, filter=filter)
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid OData Query")
    else:
        try:
            return crud.uip_session.get_multi(db=db, skip=skip, limit=top)
        except Exception as e:
            raise HTTPException(status_code=503, detail="Error retrieving data")


# --------------------------------
# --------------- Auth Stuff
# ------------------------------
@router.post("/auth", response_model=None, status_code=201)
def fetchtoken() -> schemas.UIPathTokenResponse:
    """Get valid auth Token from UIPath, OAuth2Flow.
    Also updates existing configs

    Args:
        db (Session, optional): _description_. Defaults to Depends(deps.get_db).

    Returns:
        token: string with the access token
    """
    try:
        resp = FetchUIPathToken()
    except Exception as e:
        logging.error(f"Exception when getting token from UIPATH {e}")
        raise HTTPException(
            status_code=409,
            detail="Could not request data to UIPath. Not authenticated",
        )
    return resp


@router.get("/auth", response_model=None, status_code=200)
def gettoken() -> Any:
    """Get valid auth Token from DB

    Args:
        db (Session, optional): _description_. Defaults to Depends(deps.get_db).

    Returns:
        token: string with the access token
    """
    try:
        token = GetUIPathToken()
    except Exception as e:
        logging.error(f"Exception when getting token from database {e}")
        raise HTTPException(
            status_code=409, detail="Could not retrieve token from database."
        )
    return token


@router.get("/teststuff", response_model=None, status_code=200)
def teststuff() -> Any:
    folderlist = [2440043, 4572440]
    app.worker.uipath.fetchsessions(fulldata=True)
