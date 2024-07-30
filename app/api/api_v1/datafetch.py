from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from uipath_orchestrator_rest.rest import ApiException

import app.worker.uipath
from app import crud, schemas
from app.core.celery_app import celery_app
from app.worker.uipath import FetchUIPathToken

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
        logger.error(f"Exception when calling FoldersApi->folders_get: {e.body}")
        raise HTTPException(status_code=409, detail=f"Could not request data to UIPath: {e.body}")
    except Exception as e:
        logger.error(f"Error when updating database: Folders: {e}")
        raise HTTPException(status_code=409, detail="Could not update database: Folders")
    return {"msg": "Request accepted"}


def validate_or_folderlist(formdata: schemas.UIPFetchPostBody) -> list[int]:
    # Helper function to avoid having to set the folderlist everytime and just assume you want to get every folder
    if not formdata.folderlist or formdata.folderlist == [0]:
        with app.worker.uipath.get_db() as db:
            folderlist = crud.uip_folder.get_multi(db=db, skip=0, limit=100)
            formdata.folderlist = [fol.Id for fol in folderlist]
    return formdata.folderlist


# -------------------------------
# ---------------Jobs------------
# -------------------------------
@router.post("/jobs", response_model=None, status_code=201)
def fetchjobs(
    formdata: schemas.UIPFetchPostBody,
    folderlist: list[int] = Depends(validate_or_folderlist),
) -> Any:
    """Get Jobs and save in DB (optional). Set formdata.cruddb to True

    Args:
        db (Session, optional): Database session. Defaults to Depends(deps.get_db).
        formdata (UIPFetchPostBody): Form Data (JSON Body)

    Returns:
        results: List of Jobs (Pydantic models)
    """

    try:
        kwargs = {
            "fulldata": formdata.fulldata,
            "upsert": formdata.upsert,
            "filter": formdata.filter,
            "folderlist": folderlist,
        }
        celery_app.send_task("app.worker.uipath.fetchjobs", kwargs=kwargs)
    except ApiException as e:
        logger.error(f"Exception when calling JobsAPI->jobs_get: {e.body}")
        raise HTTPException(status_code=409, detail=f"Could not request data to UIPath: {e.body}")
    except Exception as e:
        logger.error(f"Error when updating database: Jobs: {e}")
        raise HTTPException(status_code=409, detail="Could not update database: Jobs.")
    return {"msg": "Request accepted"}


# -------------------------------
# ------------Processes---------
# -------------------------------
@router.post("/processes", response_model=None, status_code=201)
def fetchprocesses(
    formdata: schemas.UIPFetchPostBody,
    folderlist: list[int] = Depends(validate_or_folderlist),
) -> Any:
    """Get Processes and save in DB (optional). Set formdata.cruddb to True

    Args:
        db (Session, optional): Database session. Defaults to Depends(deps.get_db).
        formdata (UIPFetchPostBody): Form Data (JSON Body)

    Returns:
        results: List of Processes (Pydantic models)
    """
    try:
        kwargs = {
            "fulldata": formdata.fulldata,
            "upsert": formdata.upsert,
            "filter": formdata.filter,
            "folderlist": folderlist,
        }
        celery_app.send_task("app.worker.uipath.fetchprocesses", kwargs=kwargs)
    except ApiException as e:
        logger.error(f"Exception when calling ReleasesAPI->releases_get: {e.body}")
        raise HTTPException(status_code=409, detail=f"Could not request data to UIPath: {e.body}")
    except Exception as e:
        logger.error(f"Error when updating database: Processes: {e}")
        raise HTTPException(status_code=409, detail="Could not update database: Processes")
    return {"msg": "Request accepted"}


# -------------------------------
# ----------QueueDefinitions---
# -------------------------------
@router.post("/queuedefinitions", response_model=None, status_code=201)
def fetchqueuedefinitions(
    formdata: schemas.UIPFetchPostBody,
    folderlist: list[int] = Depends(validate_or_folderlist),
) -> Any:
    """Get Queue Definitions and save in DB (optional). Set formdata.cruddb to True

    Args:
        db (Session, optional): Database session. Defaults to Depends(deps.get_db).
        formdata (UIPFetchPostBody): Form Data (JSON Body)

    Returns:
        results: List of QueueDefinitions (Pydantic models)
    """
    try:
        kwargs = {
            "fulldata": formdata.fulldata,
            "upsert": formdata.upsert,
            "filter": formdata.filter,
            "folderlist": folderlist,
        }
        celery_app.send_task("app.worker.uipath.fetchqueuedefinitions", kwargs=kwargs)
    except ApiException as e:
        logger.error(f"Exception when calling QueueDefinitionsAPI->queuedefinitions_get {e.body}")
        raise HTTPException(status_code=409, detail=f"Could not request data to UIPath: {e.body}")
    except Exception as e:
        logger.error(f"Error when updating database: Processes: {e}")
        raise HTTPException(status_code=409, detail="Could not update database: QueueDefinitions")
    return {"msg": "Request accepted"}


# -------------------------------
# -------QueueItems--------------
# -------------------------------
@router.post("/queueitems", response_model=None, status_code=201)
def fetchqueueitems(
    formdata: schemas.UIPFetchPostBody,
    folderlist: list[int] = Depends(validate_or_folderlist),
) -> Any:
    """Get QueueItems and save in DB (optional). Set formdata.cruddb to True

    Args:
        db (Session, optional): Database session. Defaults to Depends(deps.get_db).
        formdata (UIPFetchPostBody): Form Data (JSON Body)

    Returns:
        results: List of QueueItems (Pydantic models)
    """
    try:
        kwargs = {
            "fulldata": formdata.fulldata,
            "upsert": formdata.upsert,
            "filter": formdata.filter,
            "folderlist": folderlist,
        }
        celery_app.send_task("app.worker.uipath.fetchqueueitems", kwargs=kwargs)
    except ApiException as e:
        logger.error(f"Exception when calling QueueItemsAPI->queueItems_get:{e.body}")
        raise HTTPException(status_code=409, detail=f"Could not request data to UIPath: {e.body}")
    except Exception as e:
        logger.error(f"Error when updating database: QueueItems: {e}")
        raise HTTPException(status_code=409, detail="Could not update database: QueueItems")
    return {"msg": "Request accepted"}


# -------------------------------
# -------QueueItemEvents-----------
# -------------------------------
@router.post("/queueitemevents", response_model=None, status_code=201)
def fetchqueueitemevents(
    formdata: schemas.UIPFetchPostBody,
    folderlist: list[int] = Depends(validate_or_folderlist),
) -> Any:
    """Get Queue Item Events and save in DB (optional). Set formdata.cruddb to True

    Args:
        db (Session, optional): Database session. Defaults to Depends(deps.get_db).
        formdata (UIPFetchPostBody): Form Data (JSON Body)

    Returns:
        results: List of QueueItemEvents (Pydantic models)
    """
    try:
        kwargs = {
            "fulldata": formdata.fulldata,
            "upsert": formdata.upsert,
            "filter": formdata.filter,
            "folderlist": folderlist,
        }
        celery_app.send_task("app.worker.uipath.fetchqueueitemevents", kwargs=kwargs)
    except ApiException as e:
        logger.error(f"Exception when calling QueueItemsAPI->queueItems_get: {e.body}")
        raise HTTPException(status_code=409, detail=f"Could not request data to UIPath: {e.body}")
    except Exception as e:
        logger.error(f"Error when updating database: QueueItemEvents: {e}")
        raise HTTPException(status_code=409, detail="Could not update database: QueueItemEvents")
    return {"msg": "Request accepted"}


# -------------------
# -----------Sessions
# --------------------
@router.post("/sessions", response_model=None, status_code=201)
def fetchsessions(
    formdata: schemas.UIPFetchPostBody,
    folderlist: list[int] = Depends(validate_or_folderlist),
) -> Any:
    """Get sessions and save in DB (optional). Set formdata.cruddb to True

    Args:
        db (Session, optional): Database session. Defaults to Depends(deps.get_db).
        formdata (UIPFetchPostBody): Form Data (JSON Body)

    Returns:
        sessions: List of sessions (Pydantic models)
    """
    try:
        kwargs = {
            "fulldata": formdata.fulldata,
            "upsert": formdata.upsert,
            "filter": formdata.filter,
            "folderlist": folderlist,
        }
        celery_app.send_task("app.worker.uipath.fetchsessions", kwargs=kwargs)
    except ApiException as e:
        logger.error(f"Exception when calling SessionsAPI->sessions_get {e.body}")
        raise HTTPException(status_code=409, detail=f"Could not request data to UIPath: {e.body}")
    except Exception as e:
        logger.error(f"Error when updating database: Sessions: {e}")
        raise HTTPException(status_code=409, detail="Could not update database: Sessions")
    return {"msg": "Request accepted"}


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
        logger.error(f"Exception when getting token from UIPATH {e}")
        raise HTTPException(
            status_code=409,
            detail="Could not request data to UIPath. Not authenticated",
        )
    return resp


@router.get("/teststuff", response_model=None, status_code=200)
def teststuff() -> Any:
    folderlist = [2440043, 4572440]
    app.worker.uipath.fetchsessions(fulldata=True)
