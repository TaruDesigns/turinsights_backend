import json
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import UUID4, BaseModel

# Schemas for UIpath API Calls


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

    def __init__(self, **data):
        for field_name, field in self.__fields__.items():
            if field.type_ is datetime and field_name in data and data[field_name] is not None:
                from datetime import timezone

                # This is to forze UTC timezones and avoid issues with dateutil.parse trying to assign timezonelocal
                data[field_name] = data[field_name].astimezone(timezone.utc)
        super().__init__(**data)

    class Config:
        allow_population_by_field_name = False
        arbitrary_types_allowed = True

    @classmethod
    def get_select_filter(self):
        return ", ".join(self.__fields__.keys())


# ----------------------------------------
class ProcessingException(BaseApiModel):
    Reason: Optional[str]
    Details: Optional[str]
    Type: Optional[str]
    AssociatedImageFilePath: Optional[str]
    CreationTime: Optional[datetime]


# ----------------------------------------
# ------FOLDER MODELS---------------
# ----------------------------------------
class FolderBase(BaseApiModel):
    """Base Model for Folders

    Args:
        BaseApiModel (_type_): _description_
    """

    Key: UUID4
    DisplayName: str
    FullyQualifiedName: str
    Description: Optional[str]
    FolderType: str
    ParentId: Optional[int]
    ParentKey: Optional[UUID4]
    Id: int


class FolderCreate(FolderBase):
    pass


class FolderUpdate(FolderBase):
    pass


class FolderGETResponse(FolderBase):
    """Use this model to parse API Responses. Use the Select odata filter"""

    pass


# ----------------------------------------
# ------QUEUE ITEM MODELS---------------
# ----------------------------------------
class QueueItemBase(BaseApiModel):
    QueueDefinitionId: int
    Status: str
    ReviewStatus: Optional[str]
    Key: UUID4
    Reference: Optional[str]
    ProcessingExceptionType: Optional[str]
    DueDate: Optional[datetime]
    RiskSlaDate: Optional[datetime]
    Priority: str
    DeferDate: Optional[datetime]
    StartProcessing: Optional[datetime]
    EndProcessing: Optional[datetime]
    RetryNumber: int
    CreationTime: datetime
    Progress: Optional[str]
    OrganizationUnitId: int
    Id: int
    ProcessingException: Optional[ProcessingException]


class QueueItemGETResponse(QueueItemBase):
    pass


class QueueItemCreate(QueueItemGETResponse):
    pass


class QueueItemGETResponseExtended(QueueItemBase):
    ReviewerUserId: Optional[int]
    SecondsInPreviousAttempts: Optional[int]
    AncestorId: Optional[int]
    SpecificContent: Optional[Dict]
    Output: Optional[Dict]
    Analytics: Optional[Dict]


class QueueItemUpdate(QueueItemGETResponseExtended):
    pass


# ----------------------------------------
# ------QUEUE ITEM EVENT MODELS---------------
# ----------------------------------------
class QueueItemEventBase(BaseApiModel):
    QueueItemId: int
    Timestamp: datetime
    Action: str
    Status: str
    Id: int


class QueueItemEventGETResponse(QueueItemEventBase):
    pass


class QueueItemEventGETResponseExtended(QueueItemEventGETResponse):
    Data: Optional[str]
    UserId: Optional[int]
    UserName: Optional[str]
    ReviewStatus: Optional[str]
    ReviewerUserId: Optional[int]
    ReviewerUserName: Optional[str]
    ExternalClientId: Optional[int]


class QueueItemEventCreate(QueueItemEventGETResponseExtended):
    pass


# QueueItemEvents are never updated


# ----------------------------------------
# ------PROCESS/RELEASE MODELS---------------
# ----------------------------------------
# I should use the "Releases" endpoint/model instead of the "Processes" one
class ProcessBase(BaseApiModel):
    Key: UUID4
    Name: str
    OrganizationUnitId: str
    Id: int
    ProcessKey: str
    ProcessVersion: str


class ProcessGETResponse(ProcessBase):
    pass


class ProcessGETResponseExtended(ProcessGETResponse):
    JobPriority: str
    Arguments: Optional[Dict]


class ProcessCreate(ProcessGETResponse):
    pass


class ProcessUpdate(ProcessGETResponseExtended):
    pass


# ----------------------------------------
# ------JOBS MODELS---------------
# ----------------------------------------
class JobBase(BaseApiModel):
    Key: UUID4
    EndTime: Optional[datetime]
    StartTime: Optional[datetime]
    ReleaseName: str
    CreationTime: datetime
    State: str
    OrganizationUnitId: int
    Id: int


class JobGETResponse(JobBase):
    pass


class JobGETResponseExtended(JobGETResponse):
    JobPriority: str
    Source: str
    SourceType: str
    Info: Optional[str]
    StartingScheduleId: Optional[int]
    InputArguments: Optional[Dict]
    OutputArguments: Optional[Dict]
    HostMachineName: Optional[str]
    PersistenceId: Optional[UUID4]
    StopStrategy: Optional[str]
    OrganizationUnitId: int
    Reference: Optional[str]
    LocalSystemAccount: Optional[str]
    OrchestratorUserIdentity: Optional[str]
    MaxExpectedRunningTimeSeconds: Optional[int]

    @classmethod
    def parse_from_swagger(cls, res_values: Dict[str, Any], attribute_map: Dict[str, str]) -> "Any":
        """Overload original because Input and OutputArguments need to be parsed"""
        mapped_values = {}
        for key, value in res_values.items():
            mapped_key = attribute_map.get(key, key)
            if mapped_key == "OutputArguments" or mapped_key == "InputArguments":
                mapped_values[mapped_key] = json.loads(value) if value is not None else None
            else:
                mapped_values[mapped_key] = value
        return cls(**mapped_values)


class JobCreate(JobGETResponse):
    pass


class JobUpdate(JobGETResponseExtended):
    pass


class JobStrategies(str, Enum):
    All = "all"
    Specific = "Specific"
    RobotCount = "RobotCount"
    JobsCount = "JobsCount"
    ModernJobsCount = "ModernJobsCount"


class JobSources(str, Enum):
    Manual = "Manual"
    Schedule = "Schedule"
    Queue = "Queue"
    StudioWeb = "StudioWeb"
    IntegrationTrigger = "IntegrationTrigger"
    StudioDesktop = "StudioDesktop"
    AutomationOpsPipelines = "AutomationOpsPipelines"
    Apps = "Apps"


class JobRuntimeTypes(str, Enum):
    NonProduction = "NonProduction"
    Unattended = "Unattended"


class StopStrategies(str, Enum):
    SoftStop = "SoftStop"
    Kill = "Kill"


class MachineRobotDto(BaseApiModel):
    MachineId: Optional[int]
    RobotId: Optional[int]


class JobPOSTStartBodyBase(BaseApiModel):
    # To be used with Jobs/UiPath.Server.Configuration.OData.StartJobs
    ReleaseKey: UUID4
    Strategy: str = JobStrategies.All  # Default
    Source: str = JobSources.IntegrationTrigger  # Default
    SpecificPriorityValue: int = 50
    RuntimeType: str = JobRuntimeTypes.Unattended
    InputArguments: Optional[Dict]


class JobPOSTStartBodyJobCount(JobPOSTStartBodyBase):
    Strategy: str = JobStrategies.JobsCount
    JobsCount: int = 1


class JobPOSTStartBodySpecific(JobPOSTStartBodyBase):
    Strategy: str = JobStrategies.Specific
    MachineRobots = List[MachineRobotDto]


class JobPOSTStopBodyBase(BaseApiModel):
    # To be used with Jobs/UiPath.Server.Configuration.OData.StartJobs
    strategy: StopStrategies = StopStrategies.SoftStop
    jobIds: List[int]


# -----------------------------------------
# ----------QUEUEDEFINITIONS---------------
# -----------------------------------------
class QueueDefinitionBase(BaseApiModel):
    Key: UUID4
    Name: str
    OrganizationUnitId: int
    Id: int


class QueueDefinitionGETResponse(QueueDefinitionBase):
    pass


class QueueDefinitionGETResponseExtended(QueueDefinitionGETResponse):
    CreationTime: datetime
    Description: Optional[str]
    AcceptAutomaticallyRetry: Optional[bool]
    EnforceUniqueReference: Optional[bool]
    Encrypted: Optional[bool]
    SpecificDataJsonSchema: Optional[str]
    OutputDataJsonSchema: Optional[str]
    AnalyticsDataJsonSchema: Optional[str]
    ProcessScheduleId: Optional[int]
    SlaInMinutes: Optional[int]
    RiskSlaInMinutes: Optional[int]
    ReleaseId: Optional[int]
    IsProcessInCurrentFolder: Optional[bool]
    FoldersCount: Optional[int]
    Tags: Optional[Dict]


class QueueDefinitionCreate(QueueDefinitionGETResponse):
    pass


class QueueDefinitionUpdate(QueueDefinitionGETResponseExtended):
    pass


# ----------------------------------------
# ------SESSION/ROBOTS MODELS---------------
# ----------------------------------------

"""Notes for endpoints:

GET /Robots 
    Doesn't work properly

/Robots/UiPath.Server.Configuration.OData.FindAllAcrossFolders
    It doesn't return folder ID or machineid for some reason. It returns RobotID at least
    It doesn't return duplicates -> "Unique" Machines configured

/Sessions/UiPath.Server.Configuration.OData.GetMachineSessionRuntimes
    Will return sessions (=connected at one point) with  the number of runtimes in use
"""


class SessionBase(BaseApiModel):
    SessionId: int
    MachineId: int
    MachineName: str
    HostMachineName: str
    RuntimeType: str
    Status: str
    IsUnresponsive: bool
    Runtimes: int
    UsedRuntimes: int
    ServiceUserName: str
    Platform: str


class SessionGETResponse(SessionBase):
    pass


class SessionGETResponseExtended(SessionGETResponse):
    # /odata
    # Sessions are machines that have actually connected to orchestrator and are licensed
    pass


class SessionCreate(SessionGETResponse):
    pass


class SessionUpdate(SessionGETResponseExtended):
    pass


# ----------------------------------------
# ------XXXX SCHEMAS---------------
# ----------------------------------------
