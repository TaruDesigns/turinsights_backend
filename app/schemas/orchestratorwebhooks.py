from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import ConfigDict, UUID4, BaseModel


class BaseApiModel(BaseModel):
    """Base pydantic model with a json parser for attribute maps.
    Don't use it directly, only use it to inherit from it.

    Args:
        BaseApiModel (BaseApiModel): Base pydantic model
    """

    @classmethod
    def parse_from_swagger(cls, res_values: Dict[str, Any], attribute_map: Dict[str, str]) -> "Any":
        mapped_values = {}
        for key, value in res_values.items():
            mapped_key = attribute_map.get(key, key)
            mapped_values[mapped_key] = value
        return cls(**mapped_values)
    model_config = ConfigDict(populate_by_name=False, arbitrary_types_allowed=True)

    @classmethod
    def get_select_filter(self):
        return ", ".join(self.__fields__.keys())


# --- Common webhook payload properties ---


class CommonProperties(BaseApiModel):
    Name: str
    Type: str
    EventId: str
    Timestamp: datetime
    TenantId: int
    UserId: int
    OrganizationUnitId: Optional[int] = None


# -- Job related properties ---
class RobotInfo(BaseApiModel):
    Id: int
    Name: str
    MachineName: str


class ReleaseInfo(BaseApiModel):
    Id: int
    Key: UUID4
    ProcessKey: str
    Name: Optional[str] = None


class JobInfo(BaseApiModel):
    Id: int
    Key: UUID4
    State: str
    StartTime: str
    EndTime: Optional[str] = None
    Info: Optional[str] = None
    OutputArguments: Optional[dict] = None
    Robot: Optional[RobotInfo] = None
    Release: Optional[ReleaseInfo] = None


class JobPayload(CommonProperties):
    Job: JobInfo


# --- Queue Item---


class QueueInfo(BaseModel):
    Id: int
    Name: str
    Description: str
    MaxNumberOfRetries: int
    AcceptAutomaticallyRetry: bool
    EnforceUniqueReference: bool


class ProcessingExceptionInfo(BaseModel):
    Reason: str
    Details: str
    Type: str


class QueueItemInfo(BaseModel):
    Id: int
    Key: UUID4
    QueueDefinitionId: int
    Status: str
    ReviewStatus: str
    ProcessingException: Optional[ProcessingExceptionInfo] = None
    Priority: str
    CreationTime: str
    StartProcessing: str
    EndProcessing: Optional[str] = None
    SecondsInPreviousAttempts: int
    RetryNumber: int
    Robot: RobotInfo
    SpecificContent: dict
    Output: Optional[dict] = None


class QueueItemPayload(CommonProperties):
    QueueItems: list[QueueItemInfo]
    Queue: QueueInfo
