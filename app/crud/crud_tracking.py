from typing import Any, Optional
import datetime
from enum import IntEnum, unique

from odata_query.sqlalchemy import apply_odata_query
from sqlalchemy import select
from sqlalchemy.orm import Session

import app.models.orchestratorapi as uipmodels
import app.models.schedulers as schedulermodels
import app.schemas.tracking as trackschemas
from app.crud.base import CRUDBase


# This is basically an internal config enum.
@unique
class TrackingKeys(IntEnum):
    QueueItemEvents: int = 1
    JobsStarted: int = 2
    QueueItemsNew: int = 3


# TrackingKeys = {"QueueItemEvents": 1, "JobsStarted": 2, "QueueItemsNew": 3}


class CRUDTrackedProcess(
    CRUDBase[
        uipmodels.TrackedProcess,
        trackschemas.TrackedProcess,
        trackschemas.TrackedProcess,
    ]
):
    def get(self, db: Session, id: Any) -> Optional[trackschemas.TrackedProcess]:
        return db.query(self.model).filter(self.model.Id == id).first()

    def get_odata(
        self, db: Session, filter: str
    ) -> Optional[trackschemas.TrackedProcess]:
        query = apply_odata_query(select(self.model), filter)
        return db.execute(query).scalars().all()


class CRUDTrackedQueue(
    CRUDBase[
        uipmodels.TrackedQueue, trackschemas.TrackedQueue, trackschemas.TrackedQueue
    ]
):
    def get(self, db: Session, id: Any) -> Optional[trackschemas.TrackedProcess]:
        return db.query(self.model).filter(self.model.Id == id).first()

    def get_odata(
        self, db: Session, filter: str
    ) -> Optional[trackschemas.TrackedQueue]:
        query = apply_odata_query(select(self.model), filter)
        return db.execute(query).scalars().all()


class CRUDSyncTimes(
    CRUDBase[
        schedulermodels.ScheduleSyncTimes,
        trackschemas.SyncTimes,
        trackschemas.SyncTimes,
    ]
):
    def get_queueitemevent(self, db: Session) -> datetime.datetime:
        return self.get(db=db, id=TrackingKeys.QueueItemEvents).TimeStamp

    def update_queueitemevent(self, db: Session, newtime: datetime.datetime) -> None:
        schematoupdate = trackschemas.SyncTimes(
            id=int(TrackingKeys.QueueItemEvents),
            TimeStamp=newtime,
            Description="QueueItemEvents",
        )
        return self.upsert(db=db, obj_in=schematoupdate)

    # TODO: JobStartTimes and all that


tracked_process = CRUDTrackedProcess(uipmodels.TrackedProcess)
tracked_queue = CRUDTrackedQueue(uipmodels.TrackedQueue)
tracked_synctimes = CRUDSyncTimes(schedulermodels.ScheduleSyncTimes)
