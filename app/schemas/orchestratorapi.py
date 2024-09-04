import json
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import UUID4, BaseModel, ConfigDict

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
        for field_name, field in self.model_fields.items():
            if field.annotation is datetime and field_name in data and data[field_name] is not None:
                from datetime import timezone

                # This is to forze UTC timezones and avoid issues with dateutil.parse trying to assign timezonelocal
                data[field_name] = data[field_name].astimezone(timezone.utc)
        super().__init__(**data)

    model_config = ConfigDict(populate_by_name=False, arbitrary_types_allowed=True)

    @classmethod
    def get_select_filter(self):
        return ", ".join(self.model_fields.keys())


# ----------------------------------------
class ProcessingExceptionSchema(BaseApiModel):
    Reason: Optional[str] = None
    Details: Optional[str] = None
    Type: Optional[str] = None
    AssociatedImageFilePath: Optional[str] = None
    CreationTime: Optional[datetime] = None


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
    Description: Optional[str] = None
    FolderType: str
    ParentId: Optional[int] = None
    ParentKey: Optional[UUID4] = None
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
    @classmethod
    def parse_from_swagger(
        cls, res_values: Dict[str, Any], attribute_map: Dict[str, str], exception_attribute_map: Dict[str, str]
    ) -> "Any":
        # Needs to override the regular function because it has embedded ProcessingException type
        mapped_values = {}
        for key, value in res_values.items():
            mapped_key = attribute_map.get(key, key)
            # Queue Item has a PRocessingException that needs to be treated differently
            if mapped_key == "ProcessingException" and value is not None:
                # Handle nested ProcessingExceptionSchema mapping
                process_excep_values = {
                    exception_attribute_map.get(nested_key, nested_key): nested_value
                    for nested_key, nested_value in value.items()
                }
                mapped_values[mapped_key] = ProcessingExceptionSchema(**process_excep_values)
            else:
                mapped_values[mapped_key] = value
        return cls(**mapped_values)

    QueueDefinitionId: int
    Status: str
    ReviewStatus: Optional[str] = None
    Key: UUID4
    Reference: Optional[str] = None
    ProcessingExceptionType: Optional[str] = None
    DueDate: Optional[datetime] = None
    RiskSlaDate: Optional[datetime] = None
    Priority: str
    DeferDate: Optional[datetime] = None
    StartProcessing: Optional[datetime] = None
    EndProcessing: Optional[datetime] = None
    RetryNumber: int
    CreationTime: datetime
    Progress: Optional[str] = None
    OrganizationUnitId: int
    Id: int
    ProcessingException: Optional[ProcessingExceptionSchema] = None


class QueueItemGETResponse(QueueItemBase):
    pass


class QueueItemCreate(QueueItemGETResponse):
    pass


class QueueItemGETResponseExtended(QueueItemBase):
    ReviewerUserId: Optional[int] = None
    SecondsInPreviousAttempts: Optional[int] = None
    AncestorId: Optional[int] = None
    SpecificContent: Optional[Dict] = None
    Output: Optional[Dict] = None
    Analytics: Optional[Dict] = None


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
    Data: Optional[str] = None
    UserId: Optional[int] = None
    UserName: Optional[str] = None
    ReviewStatus: Optional[str] = None
    ReviewerUserId: Optional[int] = None
    ReviewerUserName: Optional[str] = None
    ExternalClientId: Optional[int] = None


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
    OrganizationUnitId: int
    Id: int
    ProcessKey: str
    ProcessVersion: str


class ProcessGETResponse(ProcessBase):
    pass


class ProcessGETResponseExtended(ProcessGETResponse):
    JobPriority: str
    Arguments: Optional[Dict] = None


class ProcessCreate(ProcessGETResponse):
    pass


class ProcessUpdate(ProcessGETResponseExtended):
    pass


# ----------------------------------------
# ------JOBS MODELS---------------
# ----------------------------------------
class JobBase(BaseApiModel):
    Key: UUID4
    EndTime: Optional[datetime] = None
    StartTime: Optional[datetime] = None
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
    Info: Optional[str] = None
    StartingScheduleId: Optional[int] = None
    InputArguments: Optional[Dict] = None
    OutputArguments: Optional[Dict] = None
    HostMachineName: Optional[str] = None
    PersistenceId: Optional[UUID4] = None
    StopStrategy: Optional[str] = None
    OrganizationUnitId: int
    Reference: Optional[str] = None
    LocalSystemAccount: Optional[str] = None
    OrchestratorUserIdentity: Optional[str] = None
    MaxExpectedRunningTimeSeconds: Optional[int] = None

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
    MachineId: Optional[int] = None
    RobotId: Optional[int] = None


class JobPOSTStartBodyBase(BaseApiModel):
    # To be used with Jobs/UiPath.Server.Configuration.OData.StartJobs
    ReleaseKey: UUID4
    Strategy: str = JobStrategies.All  # Default
    Source: str = JobSources.IntegrationTrigger  # Default
    SpecificPriorityValue: int = 50
    RuntimeType: str = JobRuntimeTypes.Unattended
    InputArguments: Optional[Dict] = None


class JobPOSTStartBodyJobCount(JobPOSTStartBodyBase):
    Strategy: str = JobStrategies.JobsCount
    JobsCount: int = 1


class JobPOSTStartBodySpecific(JobPOSTStartBodyBase):
    Strategy: str = JobStrategies.Specific
    MachineRobots: List[MachineRobotDto]


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
    Description: Optional[str] = None
    AcceptAutomaticallyRetry: Optional[bool] = None
    EnforceUniqueReference: Optional[bool] = None
    Encrypted: Optional[bool] = None
    SpecificDataJsonSchema: Optional[str] = None
    OutputDataJsonSchema: Optional[str] = None
    AnalyticsDataJsonSchema: Optional[str] = None
    ProcessScheduleId: Optional[int] = None
    SlaInMinutes: Optional[int] = None
    RiskSlaInMinutes: Optional[int] = None
    ReleaseId: Optional[int] = None
    IsProcessInCurrentFolder: Optional[bool] = None
    FoldersCount: Optional[int] = None
    Tags: Union[Optional[Dict], Optional[List[str]]] = None


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
