"""This file stores the celery tasks for the uipath data refresh (calling the API)
Note that the functions can also be used directly and they return the results from calling the API"""

# Standard Library Imports

import asyncio
import functools
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

# External Dependencies
from sqlalchemy.orm import Session
from uipath_orchestrator_rest import Configuration
from uipath_orchestrator_rest.rest import ApiException

from app import crud, schemas

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
from app.crud.base import CRUDBase
from app.db.session import get_db, get_db_async

executor = ThreadPoolExecutor(max_workers=20)


async def _CRUDHelper_async(
    obj_in: list[schemas.BaseApiModel],
    crudobject: CRUDBase,
    upsert: bool = True,
):
    """CRUD Helper to reuse in other functions asynchronously.
    Note, because it's async, each threadpool will get its own db session."""

    async def process_object(obj):
        async with get_db_async() as db:
            if upsert:
                return await crudobject.upsert_async(db=db, obj_in=obj)
            else:
                return await crudobject.create_safe_async(db=db, obj_in=obj)

    tasks = [process_object(ob) for ob in obj_in]
    results = await asyncio.gather(*tasks)
    return results


def _CRUDHelper(
    obj_in: list[schemas.BaseApiModel],
    crudobject: CRUDBase,
    upsert: bool = True,
    db: Session | None = None,
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
        list[objSchema]: List of items
    """
    return [objSchema.parse_from_swagger(obj.to_dict(), obj.attribute_map) for obj in response.value]


def _APIResToListQueueItem(response, objSchema):
    """Helper function to make a list of pydantic models from API Response

    Args:
        response (_type_): API Client Response
        objSchema (_type_): Pydantic Model

    Returns:
        list[objSchema]: List of items
    """
    res = []
    for obj in response.value:
        base_map = obj.attribute_map
        if obj.processing_exception is not None:
            excep_map = obj.processing_exception.attribute_map
        else:
            excep_map = None
        parsed = objSchema.parse_from_swagger(obj.to_dict(), base_map, excep_map)
        res.append(parsed)
    return res


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
        list[objSchema]: List of items
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
    Fetches a new token and update the "config" setting, deleting old tokens as well

    Returns:
        UIPathTokenResponse: Pydantic model with all the parameters from repsonse (access token, expiration)
    """
    logger.info("Refreshing token")
    response = oauth2_session.fetch_token(url=settings.UIP_AUTH_TOKENURL, grant_type=settings.UIP_GRANT_TYPE)
    tokenresponse = schemas.UIPathTokenResponse.parse_obj(response)
    # We update the UIPConfig variable
    if uipclient_config is not None:
        uipclient_config.access_token = tokenresponse.access_token
    with get_db() as db:
        crud.uipath_token.upsert(db=db, obj_in=tokenresponse)
        crud.uipath_token.remove_expired(db=db)
    logger.info("Token Updated")
    return tokenresponse


@celery_app.task(acks_late=True)
def GetUIPathToken(uipclient_config: Configuration = uipclient_config) -> str:
    """Returns uipath token (bare string) from database

    Args:
        uipclient_config (Configuration, optional): _description_. Defaults to uipclient_config.

    Returns:
        str: Access token (Bearer)
    """
    with get_db() as db:
        token: str = crud.uipath_token.get(db=db)
    uipclient_config.access_token = token
    return token


@celery_app.task(acks_late=True)
def fetchfolders(upsert: bool = True, fulldata: bool = True) -> Any:
    """Get folders and save in DB
    Args:
        db (Session, optional): Database session. Defaults to Depends(deps.get_db).
        formdata (UIPFetchPostBody): Form Data (JSON Body)

    Returns:
        folderlist: List of Folders (Pydantic models)
    """
    logger.info("Refreshing folders")
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
        logger.info(f"Retrieved Folders API Info")
    except ApiException as e:
        logger.error(f"Exception when calling FoldersApi->folders_get: {e.body}")
        raise e
    try:
        crudobject = crud.uip_folder
        with get_db() as db:
            _CRUDHelper(crudobject=crudobject, upsert=upsert, obj_in=folderlist, db=db)
        logger.info("Folder info stored in DB")
    except Exception as e:
        logger.error(f"Error when updating database: Folders: {e}")
        raise e
    logger.info("Folders refreshed")
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
    """Get Jobs and save in DB

    Args:
        db (Session, optional): Database session. Defaults to Depends(deps.get_db).
        formdata (UIPFetchPostBody): Form Data (JSON Body)

    Returns:
        results: List of Jobs (Pydantic models)
    """
    logger.info("Refreshing jobs")
    if fulldata:
        objSchema = schemas.JobGETResponseExtended
    else:
        objSchema = schemas.JobGETResponse
    select = objSchema.get_select_filter()
    folderlist = validate_or_default_folderlist(folderlist)
    filter = filter if filter else "Id ne 0"  # This is just a hack to avoid having to duplicate code
    with get_db() as db:
        _FolderChecker(db=db, folders=folderlist)
        results = []
        if synctimes:
            # Sync request -> use latest sync time
            lastsynctime = crud.tracked_synctimes.get_jobsstarted(db=db)
            filter = f"CreationTime gt {lastsynctime.isoformat()}Z" if lastsynctime else None
            task_sync_time = datetime.now()
        for folder in folderlist:  # folderlist will already be the IDs
            try:
                jobs = uipclient_jobs.jobs_get(
                    select=select,
                    filter=filter,
                    x_uipath_organization_unit_id=folder,
                )
                logger.info(f"Retrieved Jobs API Info for folder: {folder}")
                joblist = _APIResToList(response=jobs, objSchema=objSchema)
                results = results + joblist
            except ApiException as e:
                logger.error(f"Exception when calling JobsAPI->jobs_get: {e.body}")
        try:
            crudobject = crud.uip_job
            _CRUDHelper(crudobject=crudobject, upsert=upsert, db=db, obj_in=results)
            logger.info("Updated local Job info")
        except Exception as e:
            logger.error(f"Error when updating database: Jobs: {e}")
    logger.info("Jobs refreshed")
    if synctimes:
        crud.tracked_synctimes.update_jobsstarted(db=db, newtime=task_sync_time)
        logger.info(f"Job Info Succesfully synced: '{filter}'")
    return results


# -------------------------------
# ------------Processes---------
# -------------------------------
@celery_app.task(acks_late=True)
def fetchprocesses(
    upsert: bool = True,
    fulldata: bool = True,
    folderlist: list[int] | None = None,
    filter: str | None = None,
) -> Any:
    """Get Processes and save in DB

    Args:
        db (Session, optional): Database session. Defaults to Depends(deps.get_db).
        formdata (UIPFetchPostBody): Form Data (JSON Body)

    Returns:
        results: List of Processes (Pydantic models)
    """
    logger.info("Refreshing processes")
    folderlist = validate_or_default_folderlist(folderlist)
    if fulldata:
        objSchema = schemas.ProcessGETResponseExtended
    else:
        objSchema = schemas.ProcessGETResponse
    select = objSchema.get_select_filter()
    filter = filter if filter else "Id ne 0"  # This is just a hack to avoid having to duplicate code
    with get_db() as db:
        _FolderChecker(db=db, folders=folderlist)
        results = []
        for folder in folderlist:  # folderlist will already be the IDs
            try:
                processes = uipclient_processes.releases_get(
                    select=select,
                    filter=filter,
                    x_uipath_organization_unit_id=folder,
                )
                logger.info(f"Retrieved Processes API Info for folder: {folder}")
                processes = _APIResToList(response=processes, objSchema=objSchema)
                results = results + processes
            except ApiException as e:
                logger.error(f"Exception when calling ReleasesAPI->releases_get: {e.body}")
        try:
            crudobject = crud.uip_process
            _CRUDHelper(crudobject=crudobject, upsert=upsert, db=db, obj_in=results)
            logger.info("Processes stored in DB")
        except Exception as e:
            logger.error(f"Error when updating database: Processes: {e}")
            raise e
    logger.info("Processes refreshed")
    return results


# -------------------------------
# ----------QueueDefinitions---
# -------------------------------
@celery_app.task(acks_late=True)
def fetchqueuedefinitions(
    upsert: bool = True,
    fulldata: bool = True,
    folderlist: list[int] | None = None,
    filter: str | None = None,
) -> Any:
    """Get Queue Definitions and save in DB (optional). Set formdata.cruddb to True

    Args:
        db (Session, optional): Database session. Defaults to Depends(deps.get_db).
        formdata (UIPFetchPostBody): Form Data (JSON Body)

    Returns:
        results: List of QueueDefinitions (Pydantic models)
    """
    logger.info("Refreshing queuedefinitions")
    if fulldata:
        objSchema = schemas.QueueDefinitionGETResponseExtended
    else:
        objSchema = schemas.QueueDefinitionGETResponse
    select = objSchema.get_select_filter()
    folderlist = validate_or_default_folderlist(folderlist)
    filter = filter if filter else "Id ne 0"  # This is just a hack to avoid having to duplicate code
    with get_db() as db:
        _FolderChecker(db=db, folders=folderlist)
        results = []
        for folder in folderlist:  # folderlist will already be the IDs
            try:
                queuedefinitions = uipclient_queuedefinitions.queue_definitions_get(
                    select=select,
                    filter=filter,
                    x_uipath_organization_unit_id=folder,
                )
                queuedefinitions = _APIResToList(response=queuedefinitions, objSchema=objSchema)
                logger.info(f"Retrieved API Info for Queue Definitoins on folder {folder}")
                results = results + queuedefinitions
            except ApiException as e:
                logger.error(f"Exception when calling QueueDefinitionsAPI->queuedefinitions_get {e.body}")
        try:
            crudobject = crud.uip_queue_definitions
            _CRUDHelper(crudobject=crudobject, upsert=upsert, db=db, obj_in=results)
            logger.info("Updated QueueDefinitions in DB")
        except Exception as e:
            logger.error(f"Error when updating database: QueueDefinitions: {e}")
            raise e
    logger.info("QueueDefinitions refreshed")
    return results


# -------------------------------
# -------QueueItems--------------
# -------------------------------


async def fetch_queue_items_async(
    upsert: bool = True,
    fulldata: bool = True,
    folderlist: list[int] | None = None,
    filter: str | None = None,
    synctimes: bool = False,
) -> Any:
    """Get QueueItems and save in DB (optional). Set formdata.cruddb to True"""

    if fulldata:
        objSchema = schemas.QueueItemGETResponseExtended
    else:
        objSchema = schemas.QueueItemGETResponse

    folderlist = validate_or_default_folderlist(folderlist)
    filter = filter if filter else "Id ne 0"
    select = objSchema.get_select_filter()
    logger.info("Refreshing Queue Items")

    with get_db() as db:
        _FolderChecker(db=db, folders=folderlist)

        results = []
        if synctimes:
            lastsynctime = crud.tracked_synctimes.get_queueitemnew(db=db)
            filter = f"StartProcessing gt {lastsynctime.isoformat()}Z" if lastsynctime else None
            task_sync_time = datetime.now()

        async def fetch_from_folder(folder):
            try:
                logger.info(f"Refreshing qitems for folder: {folder}")
                # Use apply_async with async_res=True, handled by asyncio's run_in_executor
                # functools.partial allows us to pass arguments to queue_items_get
                queueitems_result = await asyncio.get_running_loop().run_in_executor(
                    executor,
                    functools.partial(
                        uipclient_queueuitems.queue_items_get,
                        select=select,
                        filter=filter,
                        x_uipath_organization_unit_id=folder,
                        async_req=True,  # Ensuring async_res=True is passed correctly
                    ),
                )

                # Wait for result completion
                queueitems_response = queueitems_result.get()

                # Process response and map it to QueueItems schema
                queueitems = _APIResToListQueueItem(response=queueitems_response, objSchema=objSchema)
                return queueitems
            except ApiException as e:
                logger.error(f"Exception when calling QueueItemsAPI->queueItems_get: {e.body}")
                raise e

        # Gather results from all folders in parallel
        logger.info(f"Refreshing folders: {folderlist}")
        tasks = [fetch_from_folder(folder) for folder in folderlist]
        folder_results = await asyncio.gather(*tasks)
        # Flatten the results to avoid having list of lists
        results = [item for sublist in folder_results for item in sublist]
        try:
            # Insert/Update database (async)
            crudobject = crud.uip_queue_item
            await _CRUDHelper_async(obj_in=results, crudobject=crudobject, upsert=upsert)
            # _CRUDHelper(crudobject=crudobject, upsert=upsert, db=db, obj_in=results)
        except Exception as e:
            logger.error(f"Error when updating database: QueueItems: {e}")
            raise e

    logger.info("Queue Items refreshed")

    if synctimes:
        crud.tracked_synctimes.update_queueitemnew(db=db, newtime=task_sync_time)
        logger.info(f"Queue Items New Info Successfully synced: '{filter}'")
    return results


@celery_app.task(bind=True, acks_late=True)
def fetchqueueitems(task=None, upsert=True, fulldata=True, folderlist=None, filter=None, synctimes=False):
    """A Celery task wrapper that runs the async fetch_queue_items_async function."""

    folderlist = folderlist or []

    async def async_task_runner():
        return await fetch_queue_items_async(
            upsert=upsert, fulldata=fulldata, folderlist=folderlist, filter=filter, synctimes=synctimes
        )

    result = asyncio.run(async_task_runner())

    return result


# -------------------------------
# -------QueueItemEvents-----------
# -------------------------------
@celery_app.task(acks_late=True)
def fetchqueueitemevents(
    upsert: bool = True,
    fulldata: bool = True,
    folderlist: list[int] | None = None,
    filter: str | None = None,
    synctimes: bool = False,
) -> Any:
    """Get Queue Item Events and save in DB (optional). Set formdata.cruddb to True

    Args:
        db (Session, optional): Database session. Defaults to Depends(deps.get_db).
        formdata (UIPFetchPostBody): Form Data (JSON Body)

    Returns:
        results: List of QueueItemEvents (Pydantic models)
    """
    logger.info("Refreshing queueitemevent")
    if fulldata:
        objSchema = schemas.QueueItemEventGETResponseExtended
    else:
        objSchema = schemas.QueueItemEventGETResponse
    folderlist = validate_or_default_folderlist(folderlist)
    select = objSchema.get_select_filter()
    filter = filter if filter else "Id ne 0"  # This is just a hack to avoid having to duplicate code
    with get_db() as db:
        _FolderChecker(db=db, folders=folderlist)
        results: list[schemas.QueueItemEventGETResponseExtended | schemas.QueueItemEventGETResponse] = []
        if synctimes:
            lastsynctime = crud.tracked_synctimes.get_queueitemevent(db=db)
            filter = f"Timestamp gt {lastsynctime.isoformat()}Z" if lastsynctime else None
            task_sync_time = datetime.now()
        for folder in folderlist:  # folderlist will already be the IDs
            try:
                queueitems = uipclient_queueuitemevents.queue_item_events_get(
                    select=select,
                    filter=filter,
                    x_uipath_organization_unit_id=folder,
                )
                queueitems = _APIResToList(response=queueitems, objSchema=objSchema)
                results = results + queueitems
            except ApiException as e:
                logger.error(f"Exception when calling QueueItemsAPI->queueItems_get: {e.body}")
                raise e

    if results:
        # IMPORTANT: Before inserting events, it is mandatory that the item exists in the database (Foreign key)
        sync_events_to_items(queueitemevents=results)
        try:
            crudobject = crud.uip_queue_item_event
            _CRUDHelper(crudobject=crudobject, upsert=upsert, db=db, obj_in=results)  # type: ignore
        except Exception as e:
            logger.error(f"Error when updating database: QueueItemEvents: {e}")
            raise e
    logger.info("Queue Item event refreshed")
    if synctimes:
        crud.tracked_synctimes.update_queueitemevent(db=db, newtime=task_sync_time)
        logger.info(f"Queue Items Event Info Succesfully synced: '{filter}'")
    return results


def sync_events_to_items(
    queueitemevents: list[schemas.QueueItemEventGETResponseExtended | schemas.QueueItemEventGETResponse],
):
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
        existing_ids, ids_not_in_db = crud.uip_queue_item.get_by_id_list_split(db=db, ids=unique_qitem_ids)
        # Get New
    if ids_not_in_db:
        logger.info("Getting new queue items")
        filter = f"Id in ({', '.join(str(x) for x in ids_not_in_db)})"
        fetchqueueitems(upsert=False, fulldata=True, filter=filter)
        logger.info("New queue items added")
    if existing_ids:
        # Update
        logger.info("Updating items")
        filter = f"Id in ({', '.join(str(x) for x in existing_ids)})"
        fetchqueueitems(upsert=True, fulldata=False, filter=filter)
        logger.info("Items updated")


# -------------------
# -----------Sessions
# --------------------
@celery_app.task(acks_late=True)
def fetchsessions(upsert: bool = True, fulldata: bool = True, filter: str | None = None) -> Any:
    """Get sessions and save in DB (optional). Set formdata.cruddb to True

    Args:
        db (Session, optional): Database session. Defaults to Depends(deps.get_db).
        formdata (UIPFetchPostBody): Form Data (JSON Body)

    Returns:
        sessions: List of sessions (Pydantic models)
    """
    logger.info("Refreshing sessions")
    filter = filter if filter else "SessionId ne 0"  # This is just a hack to avoid having to duplicate code
    if fulldata:
        objSchema = schemas.SessionGETResponseExtended
    else:
        objSchema = schemas.SessionGETResponse
    select = objSchema.get_select_filter()
    runtime_type = "Unattended"  # TODO Settings?
    with get_db() as db:
        try:
            sessions = uipclient_sessions.sessions_get_machine_session_runtimes(
                select=select, filter=filter, runtime_type=runtime_type
            )
            sessions = _APIResToList(response=sessions, objSchema=objSchema)
            logger.info("Sessions API INfo retrieved")
        except ApiException as e:
            logger.error(f"Exception when calling SessionsAPI->sessions_get {e.body}")
            raise e
        try:
            crudobject = crud.uip_session
            _CRUDHelper(crudobject=crudobject, upsert=upsert, db=db, obj_in=sessions)
            logger.info("Sessions updated in DB")
        except Exception as e:
            logger.error(f"Error when updating database: Sessions: {e}")
            raise e
    logger.info("sessions refreshed")
    return sessions
    logger.info("sessions refreshed")
    return sessions
