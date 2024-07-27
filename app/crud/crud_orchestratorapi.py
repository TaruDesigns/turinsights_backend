from typing import Any, Optional

from odata_query.sqlalchemy import apply_odata_query
from sqlalchemy import select
from sqlalchemy.orm import Session

import app.models.orchestratorapi as uipmodels
import app.schemas.orchestratorapi as uipschemas
from app.crud.base import CRUDBase


class CRUDFolder(
    CRUDBase[uipmodels.Folder, uipschemas.FolderCreate, uipschemas.FolderCreate]
):
    def get_by_fullyqualifiedname(
        self, db: Session, *, fullyqualifiedname: str
    ) -> Optional[uipmodels.Folder]:
        return (
            db.query(uipmodels.Folder)
            .filter(uipmodels.Folder.FullyQualifiedName == fullyqualifiedname)
            .first()
        )

    def get(self, db: Session, id: Any) -> Optional[uipmodels.Folder]:
        return db.query(self.model).filter(self.model.Id == id).first()

    def get_odata(self, db: Session, filter: str) -> Optional[uipmodels.Folder]:
        query = apply_odata_query(select(self.model), filter)
        return db.execute(query).scalars().all()


class CRUDQueueItem(
    CRUDBase[
        uipmodels.QueueItem, uipschemas.QueueItemCreate, uipschemas.QueueItemUpdate
    ]
):
    def get_by_reference(
        self, db: Session, *, reference: str
    ) -> Optional[uipmodels.QueueItem]:
        return (
            db.query(uipmodels.QueueItem)
            .filter(uipmodels.QueueItem.Reference == reference)
            .first()
        )

    def get(self, db: Session, id: Any) -> Optional[uipmodels.QueueItem]:
        return db.query(self.model).filter(self.model.Id == id).first()

    def get_odata(self, db: Session, filter: str) -> Optional[uipmodels.QueueItem]:
        query = apply_odata_query(select(self.model), filter)
        return db.execute(query).scalars().all()


class CRUDQueueItemEvent(
    CRUDBase[
        uipmodels.QueueItemEvent,
        uipschemas.QueueItemEventCreate,
        uipschemas.QueueItemEventCreate,
    ]
):
    def justpass(
        self, db: Session, *, fullyqualifiedname: str
    ) -> Optional[uipmodels.QueueItemEvent]:
        pass

    def get(self, db: Session, id: Any) -> Optional[uipmodels.QueueItemEvent]:
        return db.query(self.model).filter(self.model.Id == id).first()

    def get_odata(self, db: Session, filter: str) -> Optional[uipmodels.QueueItemEvent]:
        query = apply_odata_query(select(self.model), filter)
        return db.execute(query).scalars().all()


class CRUDQueueDefinitions(
    CRUDBase[
        uipmodels.QueueDefinitions,
        uipschemas.QueueDefinitionCreate,
        uipschemas.QueueDefinitionUpdate,
    ]
):
    def justpass(
        self, db: Session, *, fullyqualifiedname: str
    ) -> Optional[uipmodels.QueueDefinitions]:
        pass

    def get(self, db: Session, id: Any) -> Optional[uipmodels.QueueDefinitions]:
        return db.query(self.model).filter(self.model.Id == id).first()

    def get_odata(
        self, db: Session, filter: str
    ) -> Optional[uipmodels.QueueDefinitions]:
        query = apply_odata_query(select(self.model), filter)
        return db.execute(query).scalars().all()


class CRUDSession(
    CRUDBase[uipmodels.Sessions, uipschemas.SessionCreate, uipschemas.SessionUpdate]
):
    def justpass(
        self, db: Session, *, fullyqualifiedname: str
    ) -> Optional[uipmodels.Sessions]:
        pass

    def get(self, db: Session, id: Any) -> Optional[uipmodels.Sessions]:
        return db.query(self.model).filter(self.model.Id == id).first()

    def get_odata(self, db: Session, filter: str) -> Optional[uipmodels.Sessions]:
        query = apply_odata_query(select(self.model), filter)
        return db.execute(query).scalars().all()


class CRUDProcess(
    CRUDBase[uipmodels.Process, uipschemas.ProcessCreate, uipschemas.ProcessUpdate]
):
    def get_by_key(self, db: Session, *, key: str) -> Optional[uipmodels.Process]:
        return db.query(uipmodels.Process).filter(uipmodels.Process.Key == key).first()

    def get(self, db: Session, id: Any) -> Optional[uipmodels.Process]:
        return db.query(self.model).filter(self.model.Id == id).first()

    def get_odata(self, db: Session, filter: str) -> Optional[uipmodels.Process]:
        query = apply_odata_query(select(self.model), filter)
        return db.execute(query).scalars().all()


class CRUDJob(CRUDBase[uipmodels.Job, uipschemas.JobCreate, uipschemas.JobUpdate]):
    def get_by_releasename(
        self, db: Session, *, releasename: str
    ) -> Optional[uipmodels.Job]:
        return (
            db.query(uipmodels.Job)
            .filter(uipmodels.Job.ReleaseName == releasename)
            .first()
        )

    def get(self, db: Session, id: Any) -> Optional[uipmodels.Job]:
        return db.query(self.model).filter(self.model.Id == id).first()

    def get_odata(self, db: Session, filter: str) -> Optional[uipmodels.Job]:
        query = apply_odata_query(select(self.model), filter)
        return db.execute(query).scalars().all()


folder = CRUDFolder(uipmodels.Folder)
queue_item = CRUDQueueItem(uipmodels.QueueItem)
queue_item_event = CRUDQueueItemEvent(uipmodels.QueueItemEvent)
queue_definitions = CRUDQueueDefinitions(uipmodels.QueueDefinitions)
process = CRUDProcess(uipmodels.Process)
job = CRUDJob(uipmodels.Job)
session = CRUDSession(uipmodels.Sessions)
