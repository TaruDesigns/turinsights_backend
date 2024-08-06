from typing import Any, Optional, Tuple

from odata_query.sqlalchemy.shorthand import apply_odata_query
from sqlalchemy import select
from sqlalchemy.orm import Session

import app.models.orchestratorapi as uipmodels
import app.schemas.orchestratorapi as uipschemas
from app.crud.base import CRUDBase


class CRUDFolder(CRUDBase[uipmodels.Folder, uipschemas.FolderCreate, uipschemas.FolderCreate]):
    def get_by_fullyqualifiedname(self, db: Session, *, fullyqualifiedname: str) -> Optional[uipmodels.Folder]:
        return db.query(uipmodels.Folder).filter(uipmodels.Folder.FullyQualifiedName == fullyqualifiedname).first()

    def get(self, db: Session, id: Any) -> Optional[uipmodels.Folder]:
        return db.query(self.model).filter(self.model.Id == id).first()

    def get_odata(self, db: Session, filter: str) -> Optional[uipmodels.Folder]:
        query = apply_odata_query(select(self.model), filter)
        return db.execute(query).scalars().all()  # type: ignore


class CRUDQueueItem(CRUDBase[uipmodels.QueueItem, uipschemas.QueueItemCreate, uipschemas.QueueItemUpdate]):
    def get_by_reference(self, db: Session, *, reference: str) -> Optional[uipmodels.QueueItem]:
        return db.query(uipmodels.QueueItem).filter(uipmodels.QueueItem.Reference == reference).first()

    def get(self, db: Session, id: Any) -> Optional[uipmodels.QueueItem]:
        return db.query(self.model).filter(self.model.Id == id).first()

    def get_odata(self, db: Session, filter: str) -> Optional[uipmodels.QueueItem]:
        query = apply_odata_query(select(self.model), filter)
        return db.execute(query).scalars().all()  # type: ignore

    def get_by_id_list_split(self, db: Session, ids: list[int]) -> Tuple[list[int], list[int]]:
        """This is a helper function to return which IDs are present in the database and which are not, based on an input list of IDs
        get_odata kind of replaces this but this one is more direct without dependencies
        Args:
            db (Session): _description_
            ids (list[int]): _description_

        Returns:
            Tuple[list[int], list[int]] | None: _description_
        """
        localquery = select(self.model.Id).where(self.model.Id.in_(ids))
        existing_ids = db.execute(localquery).scalars().all()
        existing_ids_set = set(existing_ids)
        all_ids_set = set(ids)
        ids_not_in_db = list(all_ids_set - existing_ids_set)
        return existing_ids, ids_not_in_db


class CRUDQueueItemEvent(
    CRUDBase[
        uipmodels.QueueItemEvent,
        uipschemas.QueueItemEventCreate,
        uipschemas.QueueItemEventCreate,
    ]
):
    def justpass(self, db: Session, *, fullyqualifiedname: str) -> Optional[uipmodels.QueueItemEvent]:
        pass

    def get(self, db: Session, id: Any) -> Optional[uipmodels.QueueItemEvent]:
        return db.query(self.model).filter(self.model.Id == id).first()

    def get_odata(self, db: Session, filter: str) -> Optional[uipmodels.QueueItemEvent]:
        query = apply_odata_query(select(self.model), filter)
        return db.execute(query).scalars().all()  # type: ignore


class CRUDQueueDefinitions(
    CRUDBase[
        uipmodels.QueueDefinitions,
        uipschemas.QueueDefinitionCreate,
        uipschemas.QueueDefinitionUpdate,
    ]
):
    def justpass(self, db: Session, *, fullyqualifiedname: str) -> Optional[uipmodels.QueueDefinitions]:
        pass

    def get(self, db: Session, id: Any) -> Optional[uipmodels.QueueDefinitions]:
        return db.query(self.model).filter(self.model.Id == id).first()

    def get_odata(self, db: Session, filter: str) -> Optional[uipmodels.QueueDefinitions]:
        query = apply_odata_query(select(self.model), filter)
        return db.execute(query).scalars().all()  # type: ignore


class CRUDSession(CRUDBase[uipmodels.Sessions, uipschemas.SessionCreate, uipschemas.SessionUpdate]):
    def justpass(self, db: Session, *, fullyqualifiedname: str) -> Optional[uipmodels.Sessions]:
        pass

    def get(self, db: Session, id: Any) -> Optional[uipmodels.Sessions]:
        return db.query(self.model).filter(self.model.Id == id).first()

    def get_odata(self, db: Session, filter: str) -> Optional[uipmodels.Sessions]:
        query = apply_odata_query(select(self.model), filter)
        return db.execute(query).scalars().all()  # type: ignore


class CRUDProcess(CRUDBase[uipmodels.Process, uipschemas.ProcessCreate, uipschemas.ProcessUpdate]):
    def get_by_key(self, db: Session, *, key: str) -> Optional[uipmodels.Process]:
        return db.query(uipmodels.Process).filter(uipmodels.Process.Key == key).first()

    def get(self, db: Session, id: Any) -> Optional[uipmodels.Process]:
        return db.query(self.model).filter(self.model.Id == id).first()

    def get_odata(self, db: Session, filter: str) -> Optional[uipmodels.Process]:
        query = apply_odata_query(select(self.model), filter)
        return db.execute(query).scalars().all()  # type: ignore


class CRUDJob(CRUDBase[uipmodels.Job, uipschemas.JobCreate, uipschemas.JobUpdate]):
    def get_by_releasename(self, db: Session, *, releasename: str) -> Optional[uipmodels.Job]:
        return db.query(uipmodels.Job).filter(uipmodels.Job.ReleaseName == releasename).first()

    def get(self, db: Session, id: Any) -> Optional[uipmodels.Job]:
        return db.query(self.model).filter(self.model.Id == id).first()

    def get_odata(self, db: Session, filter: str) -> list[uipmodels.Job]:
        query = apply_odata_query(select(self.model), filter)
        return db.execute(query).scalars().all()  # type: ignore

    def get_unfinished_jobid(self, db: Session) -> list[int] | None:
        # Returns the Ids for the jobs that are not in a finished state so that they can be polled
        finished_states = ["Faulted", "Successful", "Stopped"]
        res = db.query(self.model.Id).filter(self.model.State.notin_(finished_states)).all()
        return [row[0] for row in res] if res else None
        ...


uip_folder = CRUDFolder(uipmodels.Folder)
uip_queue_item = CRUDQueueItem(uipmodels.QueueItem)
uip_queue_item_event = CRUDQueueItemEvent(uipmodels.QueueItemEvent)
uip_queue_definitions = CRUDQueueDefinitions(uipmodels.QueueDefinitions)
uip_process = CRUDProcess(uipmodels.Process)
uip_job = CRUDJob(uipmodels.Job)
uip_session = CRUDSession(uipmodels.Sessions)
