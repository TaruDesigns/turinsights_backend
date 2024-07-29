# Standard Library Imports
import logging
from contextlib import contextmanager
from datetime import datetime
from enum import StrEnum, unique
from typing import Any, Generator, List, Optional

from celery import Task
from celery.exceptions import Ignore
from celery.signals import after_setup_task_logger

# Third-Party Imports
from raven import Client
from sqlalchemy.exc import IntegrityError

# External Dependencies
from sqlalchemy.orm import Session
from uipath_orchestrator_rest import Configuration
from uipath_orchestrator_rest.rest import ApiException

from app import crud, models, schemas

# Project-Specific Imports
from app.core.celery_app import celery_app
from app.core.config import settings
from app.core.uipapiconfig import (
    oauth2_session,
    uipclient_config,
    uipclient_folders,
    uipclient_jobs,
    uipclient_processes,
    uipclient_queuedefinitions,
    uipclient_queueuitemevents,
    uipclient_queueuitems,
    uipclient_sessions,
)
from app.crud import tracked_synctimes, uip_folder
from app.crud.base import CRUDBase
from app.db.session import SessionLocal, get_db

client_sentry = Client(settings.SENTRY_DSN)


def _CRUDHelper(
    obj_in: List[schemas.BaseApiModel],
    crudobject: CRUDBase,
    upsert: bool = True,
    db: Session = None,
):
    """CRUD Helper to reuse in other functions.

    Returns:
        True if values were added
    """
    if db is None:
        raise ValueError("No DB Object provided")
    if upsert:
        for ob in obj_in:  # TODO insert all at once?
            crudobject.upsert(db=db, obj_in=ob)
    else:
        for ob in obj_in:
            crudobject.create_safe(db=db, obj_in=ob)


def _APIResToList(response, objSchema):
    """Helper function to make a list of pydantic models from API Response

    Args:
        response (_type_): API Client Response
        objSchema (_type_): Pydantic Model

    Returns:
        List[objSchema]: List of items
    """
    return [
        objSchema.parse_from_swagger(obj.to_dict(), obj.attribute_map)
        for obj in response.value
    ]


def validate_or_default_folderlist(folderlist: list[int] | None) -> list[int]:
    # Helper function to avoid having to set the folderlist everytime and just assume you want to get every folder
    if not folderlist or folderlist == [0]:
        with get_db() as db:
            default_folderlist = crud.uip_folder.get_multi(db=db, skip=0, limit=100)
            folderlist = [fol.Id for fol in default_folderlist]
    return folderlist


def _FolderChecker(folders: list[int] | None, db: Session | None = None):
    """Helper function to validate that the folders indicated do exist in the database

    Args:
        response (_type_): API Client Response
        objSchema (_type_): Pydantic Model

    Returns:
        List[objSchema]: List of items
    """
    if folders is None:
        raise ValueError("No folder list was provided")
    if db is None:
        raise ValueError("No DB Object provided")
    for folderid in folders:
        if crud.uip_folder.get(db=db, id=folderid) is None:
            raise ValueError(f"Folder not valid: No data for id: {folderid}")


@celery_app.task(acks_late=True)
def FetchUIPathToken(uipclient_config=uipclient_config) -> schemas.UIPathTokenResponse:
    """Fetch UIPath Access Token.
    Helper function to fetch token and update the "config" setting

    Returns:
        UIPathTokenResponse: Pydantic model with all the parameters from repsonse (access token, expiration)
    """
    logging.info("Refreshing token")
    response = oauth2_session.fetch_token(
        url=settings.UIP_AUTH_TOKENURL, grant_type=settings.UIP_GRANT_TYPE
    )
    tokenresponse = schemas.UIPathTokenResponse.parse_obj(response)
    # We update the UIPConfig variable
    if uipclient_config is not None:
        uipclient_config.access_token = tokenresponse.access_token
    with get_db() as db:
        crud.uipath_token.create(db=db, obj_in=tokenresponse)
    logging.info("Token Updated")
    return "Token Updated"


@celery_app.task(acks_late=True)
def GetUIPathToken(uipclient_config: Configuration = uipclient_config):
    with get_db() as db:
        token = crud.uipath_token.get(db=db)
    uipclient_config.access_token = token
    return token


@celery_app.task(acks_late=True)
def fetchfolders(upsert: bool = True, fulldata: bool = True) -> Any:
    """Get folders and save in DB (optional). Set formdata.cruddb to True

    Args:
        db (Session, optional): Database session. Defaults to Depends(deps.get_db).
        formdata (UIPFetchPostBody): Form Data (JSON Body)

    Returns:
        folderlist: List of Folders (Pydantic models)
    """
    logging.info("Refreshing folders")
    GetUIPathToken(uipclient_config=uipclient_config)
    if fulldata:
        objSchema = schemas.FolderGETResponse  # Extended
    else:
        objSchema = schemas.FolderGETResponse
    try:
        # Gets folders.
        select = objSchema.get_select_filter()
        folders = uipclient_folders.folders_get(select=select)
        folderlist = _APIResToList(response=folders, objSchema=objSchema)
    except ApiException as e:
        logging.error(f"Exception when calling FoldersApi->folders_get: {e.body}")
        raise e
    try:
        crudobject = crud.uip_folder
        with get_db() as db:
            _CRUDHelper(crudobject=crudobject, upsert=upsert, obj_in=folderlist, db=db)
    except Exception as e:
        logging.error(f"Error when updating database: Folders: {e}")
        raise e
    logging.info("Folders refreshed")
    return folderlist


# -------------------------------
# ---------------Jobs------------
# -------------------------------
@celery_app.task(acks_late=True)
def fetchjobs(
    upsert: bool = True,
    fulldata: bool = True,
    folderlist: list[int] | None = None,
    filter: str | None = None,
    synctimes: bool = False,
) -> Any:
    """Get Jobs and save in DB (optional). Set formdata.cruddb to True

    Args:
        db (Session, optional): Database session. Defaults to Depends(deps.get_db).
        formdata (UIPFetchPostBody): Form Data (JSON Body)

    Returns:
        results: List of Jobs (Pydantic models)
    """
    logging.info("Refreshing jobs")
    if fulldata:
        objSchema = schemas.JobGETResponseExtended
    else:
        objSchema = schemas.JobGETResponse
    folderlist = validate_or_default_folderlist(folderlist)
    with get_db() as db:
        _FolderChecker(db=db, folders=folderlist)
        select = objSchema.get_select_filter()
        results = []
        if synctimes:
            lastsynctime = tracked_synctimes.get_jobsstarted(db=db)
            filter = (
                f"CreationTime gt {lastsynctime.isoformat()}Z" if lastsynctime else None
            )
            task_sync_time = datetime.now()
        for folder in folderlist:  # folderlist will already be the IDs
            try:
                if filter:
                    jobs = uipclient_jobs.jobs_get(
                        select=select,
                        filter=filter,
                        x_uipath_organization_unit_id=folder,
                    )
                else:
                    jobs = uipclient_jobs.jobs_get(
                        select=select, x_uipath_organization_unit_id=folder
                    )
                joblist = _APIResToList(response=jobs, objSchema=objSchema)
                results = results + joblist
            except ApiException as e:
                logging.error(f"Exception when calling JobsAPI->jobs_get: {e.body}")
                raise e
            try:
                crudobject = crud.uip_job
                _CRUDHelper(crudobject=crudobject, upsert=upsert, db=db, obj_in=joblist)
            except Exception as e:
                logging.error(f"Error when updating database: Jobs: {e}")
                raise e
    logging.info("Jobs refreshed")
    if synctimes:
        tracked_synctimes.update_jobsstarted(db=db, newtime=task_sync_time)
        logging.info(f"Job Info Succesfully synced: '{filter}'")
    return results


# -------------------------------
# ------------Processes---------
# -------------------------------
@celery_app.task(acks_late=True)
def fetchprocesses(
    upsert: bool = True,
    fulldata: bool = True,
    folderlist: List[int] = None,
    filter: str = None,
) -> Any:
    """Get Processes and save in DB (optional). Set formdata.cruddb to True

    Args:
        db (Session, optional): Database session. Defaults to Depends(deps.get_db).
        formdata (UIPFetchPostBody): Form Data (JSON Body)

    Returns:
        results: List of Processes (Pydantic models)
    """
    logging.info("Refreshing processes")
    with get_db() as db:
        _FolderChecker(db=db, folders=folderlist)
        if fulldata:
            objSchema = schemas.ProcessGETResponseExtended
        else:
            objSchema = schemas.ProcessGETResponse
        select = objSchema.get_select_filter()
        results = []
        for folder in folderlist:  # folderlist will already be the IDs
            try:
                if filter:
                    processes = uipclient_processes.releases_get(
                        select=select,
                        filter=filter,
                        x_uipath_organization_unit_id=folder,
                    )
                else:
                    processes = uipclient_processes.releases_get(
                        select=select, x_uipath_organization_unit_id=folder
                    )
                processes = _APIResToList(response=processes, objSchema=objSchema)
                results = results + processes
            except ApiException as e:
                logging.error(
                    f"Exception when calling ReleasesAPI->releases_get: {e.body}"
                )
                raise e
            try:
                crudobject = crud.uip_process
                _CRUDHelper(
                    crudobject=crudobject, upsert=upsert, db=db, obj_in=processes
                )
            except Exception as e:
                logging.error(f"Error when updating database: Processes: {e}")
                raise e
    logging.info("Processes refreshed")
    return results


# -------------------------------
# ----------QueueDefinitions---
# -------------------------------
@celery_app.task(acks_late=True)
def fetchqueuedefinitions(
    upsert: bool = True,
    fulldata: bool = True,
    folderlist: List[int] = None,
    filter: str = None,
) -> Any:
    """Get Queue Definitions and save in DB (optional). Set formdata.cruddb to True

    Args:
        db (Session, optional): Database session. Defaults to Depends(deps.get_db).
        formdata (UIPFetchPostBody): Form Data (JSON Body)

    Returns:
        results: List of QueueDefinitions (Pydantic models)
    """
    logging.info("Refreshing queuedefinitions")
    with get_db() as db:
        _FolderChecker(db=db, folders=folderlist)
        if fulldata:
            objSchema = schemas.QueueDefinitionGETResponseExtended
        else:
            objSchema = schemas.QueueDefinitionGETResponse
        select = objSchema.get_select_filter()
        results = []
        for folder in folderlist:  # folderlist will already be the IDs
            try:
                if filter:
                    queuedefinitions = uipclient_queuedefinitions.queue_definitions_get(
                        select=select,
                        filter=filter,
                        x_uipath_organization_unit_id=folder,
                    )
                else:
                    queuedefinitions = uipclient_queuedefinitions.queue_definitions_get(
                        select=select, x_uipath_organization_unit_id=folder
                    )
                queuedefinitions = _APIResToList(
                    response=queuedefinitions, objSchema=objSchema
                )
                results = results + queuedefinitions
            except ApiException as e:
                logging.error(
                    f"Exception when calling QueueDefinitionsAPI->queuedefinitions_get {e.body}"
                )
                raise e
            try:
                crudobject = crud.uip_queue_definitions
                _CRUDHelper(
                    crudobject=crudobject, upsert=upsert, db=db, obj_in=queuedefinitions
                )
            except Exception as e:
                logging.error(f"Error when updating database: Processes: {e}")
                raise e
    logging.info("QueueDefinitions refreshed")
    return results


# -------------------------------
# -------QueueItems--------------
# -------------------------------
@celery_app.task(acks_late=True)
def fetchqueueitems(
    upsert: bool = True,
    fulldata: bool = True,
    folderlist: List[int] = None,
    filter: str = None,
    synctimes: bool = False,
) -> Any:
    """Get QueueItems and save in DB (optional). Set formdata.cruddb to True

    Args:
        db (Session, optional): Database session. Defaults to Depends(deps.get_db).
        formdata (UIPFetchPostBody): Form Data (JSON Body)

    Returns:
        results: List of QueueItems (Pydantic models)
    """
    if fulldata:
        objSchema = schemas.QueueItemGETResponseExtended
    else:
        objSchema = schemas.QueueItemGETResponse
    folderlist = validate_or_default_folderlist(folderlist)
    logging.info("Refreshing Queue Items")
    with get_db() as db:
        _FolderChecker(db=db, folders=folderlist)
        select = objSchema.get_select_filter()
        results = []
        if synctimes:
            lastsynctime = tracked_synctimes.get_queueitemnew(db=db)
            filter = (
                f"StartProcessing gt {lastsynctime.isoformat()}Z"
                if lastsynctime
                else None
            )
            task_sync_time = datetime.now()
        for folder in folderlist:  # folderlist will already be the IDs
            try:
                if filter:
                    queueitems = uipclient_queueuitems.queue_items_get(
                        select=select,
                        filter=filter,
                        x_uipath_organization_unit_id=folder,
                    )
                else:
                    queueitems = uipclient_queueuitems.queue_items_get(
                        select=select, x_uipath_organization_unit_id=folder
                    )
                queueitems = _APIResToList(response=queueitems, objSchema=objSchema)
                results = results + queueitems
            except ApiException as e:
                logging.error(
                    f"Exception when calling QueueItemsAPI->queueItems_get:{e.body}"
                )
                raise e
            try:
                crudobject = crud.uip_queue_item
                _CRUDHelper(
                    crudobject=crudobject, upsert=upsert, db=db, obj_in=queueitems
                )
            except Exception as e:
                logging.error(f"Error when updating database: QueueItems: {e}")
                raise e
    logging.info("Queue Items refreshed")
    if synctimes:
        tracked_synctimes.update_queueitemnew(db=db, newtime=task_sync_time)
        logging.info(f"Queue Items New Info Succesfully synced: '{filter}'")
    return results


# -------------------------------
# -------QueueItemEvents-----------
# -------------------------------
@celery_app.task(acks_late=True)
def fetchqueueitemevents(
    upsert: bool = True,
    fulldata: bool = True,
    folderlist: List[int] = None,
    filter: str = None,
    synctimes: bool = False,
) -> Any:
    """Get Queue Item Events and save in DB (optional). Set formdata.cruddb to True

    Args:
        db (Session, optional): Database session. Defaults to Depends(deps.get_db).
        formdata (UIPFetchPostBody): Form Data (JSON Body)

    Returns:
        results: List of QueueItemEvents (Pydantic models)
    """
    logging.info("Refreshing queueitemevent")
    if fulldata:
        objSchema = schemas.QueueItemEventGETResponseExtended
    else:
        objSchema = schemas.QueueItemEventGETResponse
    folderlist = validate_or_default_folderlist(folderlist)
    with get_db() as db:
        _FolderChecker(db=db, folders=folderlist)
        select = objSchema.get_select_filter()
        results: list[
            schemas.QueueItemEventGETResponseExtended
            | schemas.QueueItemEventGETResponse
        ] = []
        if synctimes:
            lastsynctime = tracked_synctimes.get_queueitemevent(db=db)
            filter = (
                f"Timestamp gt {lastsynctime.isoformat()}Z" if lastsynctime else None
            )
            task_sync_time = datetime.now()
        for folder in folderlist:  # folderlist will already be the IDs
            try:
                if filter:
                    queueitems = uipclient_queueuitemevents.queue_item_events_get(
                        select=select,
                        filter=filter,
                        x_uipath_organization_unit_id=folder,
                    )
                else:
                    queueitems = uipclient_queueuitemevents.queue_item_events_get(
                        select=select, x_uipath_organization_unit_id=folder
                    )
                queueitems = _APIResToList(response=queueitems, objSchema=objSchema)
                results = results + queueitems
            except ApiException as e:
                logging.error(
                    f"Exception when calling QueueItemsAPI->queueItems_get: {e.body}"
                )
                raise e
            try:
                crudobject = crud.uip_queue_item_event
                _CRUDHelper(
                    crudobject=crudobject, upsert=upsert, db=db, obj_in=queueitems
                )
            except Exception as e:
                logging.error(f"Error when updating database: QueueItemEvents: {e}")
                raise e
    logging.info("Queue Item event refreshed")
    if synctimes:
        tracked_synctimes.update_queueitemevent(db=db, newtime=task_sync_time)
        logging.info(f"Queue Items Event Info Succesfully synced: '{filter}'")
    if results:
        sync_events_to_items(queueitemevents=results)
    return results


def sync_events_to_items(queueitemevents: schemas.QueueItemEventGETResponse = None):
    """This function syncs the queueitemevents to the state in the DB The business logic is:
        - If the item is NOT in the database, it needs to be inserted.
            In order to do that, we retrieve its full data (API -> GetQueueItem) and upsert
        - If the item IS in the database, we retrieve the latest data,
            selecting so we only get the data we need from the API for performance (no fulldata)
        Note that in order to update the QueueItemData we don't actually hit the database for each and every QueueItemEvent
        because we only care about the latest data.
        We also don't care if the item is in its final state (eg, multiple Events)
            but the Database never saw it (eg the QueueItemId is not found)
            because we will just get the fulldata (including its final state) anyway
        But we have previously inserted ALL the QueueItemEvents in its table.

        #TODO: This could in theory be another celery task, but one that is ONLY launched after retrieving Events.

    Args:
        queueitemevents (schemas.QueueItemEventGETResponse, optional): _description_. Defaults to None.
    """

    #
    unique_qitem_ids = list(set(item.QueueItemId for item in queueitemevents))
    with get_db() as db:
        # Split queueitemevents into two buckets: One for items that are not in DB and one that are in DB (based on QueueItemId)
        existing_ids, ids_not_in_db = crud.uip_queue_item.get_by_id_list_split(
            db=db, ids=unique_qitem_ids
        )
        # Get New
    logging.info("Getting new queue items")
    filter = f"Id in ({', '.join(str(x) for x in ids_not_in_db)})"
    fetchqueueitems(upsert=False, fulldata=True, filter=filter)
    logging.info("New queue items added")
    # Update
    logging.info("Updating items")
    filter = f"Id in ({', '.join(str(x) for x in existing_ids)})"
    fetchqueueitems(upsert=True, fulldata=False, filter=filter)
    logging.info("Items updated")


# -------------------
# -----------Sessions
# --------------------
@celery_app.task(acks_late=True)
def fetchsessions(
    upsert: bool = True, fulldata: bool = True, filter: str = None
) -> Any:
    """Get sessions and save in DB (optional). Set formdata.cruddb to True

    Args:
        db (Session, optional): Database session. Defaults to Depends(deps.get_db).
        formdata (UIPFetchPostBody): Form Data (JSON Body)

    Returns:
        sessions: List of sessions (Pydantic models)
    """
    logging.info("Refreshing sessions")
    with get_db() as db:
        if fulldata:
            objSchema = schemas.SessionGETResponseExtended
        else:
            objSchema = schemas.SessionGETResponse
        select = objSchema.get_select_filter()
        runtime_type = "Unattended"
        try:
            if filter:
                sessions = uipclient_sessions.sessions_get_machine_session_runtimes(
                    select=select, filter=filter, runtime_type=runtime_type
                )
            else:
                sessions = uipclient_sessions.sessions_get_machine_session_runtimes(
                    select=select, runtime_type=runtime_type
                )
            sessions = _APIResToList(response=sessions, objSchema=objSchema)
        except ApiException as e:
            logging.error(f"Exception when calling SessionsAPI->sessions_get {e.body}")
            raise e
        try:
            crudobject = crud.uip_session
            _CRUDHelper(crudobject=crudobject, upsert=upsert, db=db, obj_in=sessions)
        except Exception as e:
            logging.error(f"Error when updating database: Sessions: {e}")
            raise e
    logging.info("sessions refreshed")
    return sessions
