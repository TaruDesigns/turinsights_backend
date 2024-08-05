import datetime
from typing import Optional

from pydantic import UUID4, BaseModel


class TrackedProcess(BaseModel):
    Id: int
    ProcessKey: UUID4
    Strategy: str
    CronJob: str
    MinRetries: int
    Enabled: bool


class TrackedQueue(BaseModel):
    Id: int
    QueueId: UUID4
    Strategy: str
    CronJob: str
    MinRetries: int
    Enabled: bool


class SyncTimes(BaseModel):
    id: int
    TimeStamp: datetime.datetime
    Description: Optional[str] = None
