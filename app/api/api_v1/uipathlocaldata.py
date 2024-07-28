import logging
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

import app.worker.uipath
from app import crud, schemas
from app.api import deps
from app.worker.uipath import FetchUIPathToken, GetUIPathToken

router = APIRouter()


# -------------------------------
# -------------Folders----------
# -------------------------------


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
