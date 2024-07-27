from __future__ import annotations

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import mapped_column, relationship

from app.db.base_class import Base


class Folder(Base):
    # Folder = OrganizationUnit
    __tablename__ = "uipath_folders"
    Id = mapped_column(Integer, primary_key=True, index=True)
    Key = mapped_column(UUID(as_uuid=True))
    DisplayName = mapped_column(String, index=True)
    FullyQualifiedName = mapped_column(String)
    Description = mapped_column(String)
    FolderType = mapped_column(String)
    ParentId = mapped_column(Integer)
    ParentKey = mapped_column(UUID(as_uuid=True))
    # Refs

    QueueDefinitions = relationship("QueueDefinitions", back_populates="Folder")
    Processes = relationship("Process", back_populates="Folder")
    QueueItems = relationship("QueueItem", back_populates="Folder")
    Jobs = relationship("Job", back_populates="Folder")


class QueueDefinitions(Base):
    __tablename__ = "uipath_queuedefinitions"
    Id = mapped_column(Integer, primary_key=True, index=True)
    Key = mapped_column(UUID(as_uuid=True))
    OrganizationUnitId = mapped_column(ForeignKey("uipath_folders.Id"))
    ReleaseId = mapped_column(Integer)  # TODO Expand and relationship
    Name = mapped_column(String)
    CreationTime = mapped_column(DateTime)
    Description = mapped_column(String)
    MaxNumberOfRetires = mapped_column(Integer)
    AcceptAutomaticallyRetry = mapped_column(Boolean)
    EnforceUniqueReference = mapped_column(Boolean)
    Encrypted = mapped_column(Boolean)
    SpecificDataJsonSchema = mapped_column(String)
    OutputDataJsonSchema = mapped_column(String)
    AnalyticsDataJsonSchema = mapped_column(String)
    ProcessScheduleId = mapped_column(Integer)
    SlaInMinutes = mapped_column(Integer)
    RiskSlaInMinutes = mapped_column(Integer)
    IsProcessInCurrentFolder = mapped_column(Boolean)
    FoldersCount = mapped_column(Integer)
    Tags = mapped_column(JSON)

    # Refs
    # Establish the relationship with Folder
    Folder = relationship("Folder", back_populates="QueueDefinitions")
    QueueItems = relationship("QueueItem", back_populates="QueueDefinition")
    Tracked = relationship("TrackedQueue", back_populates="Queue")


class TrackedQueue(Base):
    """Model for queue definitions(queue items) tracking strategies"""

    __tablename__ = "tracked_queues"
    Id = mapped_column(Integer, primary_key=True, index=True)
    QueueId = mapped_column(ForeignKey("uipath_queuedefinitions.Id"))
    Strategy = mapped_column(String)
    CronJob = mapped_column(String)
    MinRetries = mapped_column(Integer)
    Enabled = mapped_column(Boolean)
    # Refs
    Queue = relationship("QueueDefinitions", back_populates="Tracked")


class Process(Base):
    __tablename__ = "uipath_processes"
    Key = mapped_column(
        UUID, primary_key=True, index=True
    )  # For starting job and whatnot, we use the Key
    Id = mapped_column(Integer)
    OrganizationUnitId = mapped_column(ForeignKey("uipath_folders.Id"))
    Name = mapped_column(String)
    JobPriority = mapped_column(String)
    ProcessKey = mapped_column(String)
    ProcessVersion = mapped_column(String)
    Arguments = mapped_column(JSON)
    # Refs
    Folder = relationship("Folder", back_populates="Processes")
    Tracked = relationship("TrackedProcess", back_populates="Process")


class TrackedProcess(Base):
    """Model for process(jobs) tracking strategies"""

    __tablename__ = "tracked_processes"
    Id = mapped_column(Integer, primary_key=True, index=True)
    ProcessKey = mapped_column(ForeignKey("uipath_processes.Key"))
    Strategy = mapped_column(String)
    CronJob = mapped_column(String)
    MinRetries = mapped_column(Integer)
    Enabled = mapped_column(Boolean)
    # Refs
    Process = relationship("Process", back_populates="Tracked")


class QueueItem(Base):
    __tablename__ = "uipath_queueitems"
    Id = mapped_column(Integer, primary_key=True, index=True)
    QueueDefinitionId = mapped_column(ForeignKey("uipath_queuedefinitions.Id"))
    ReviewerUserId = mapped_column(Integer)
    AncestorId = mapped_column(Integer)
    OrganizationUnitId = mapped_column(ForeignKey("uipath_folders.Id"))
    Status = mapped_column(String)
    ReviewStatus = mapped_column(String)
    Key = mapped_column(UUID(as_uuid=True))
    Reference = mapped_column(String)
    ProcessingExceptionType = mapped_column(String)
    DueDate = mapped_column(DateTime)
    RiskSlaDate = mapped_column(DateTime)
    Priority = mapped_column(String)
    DeferDate = mapped_column(DateTime)
    StartProcessing = mapped_column(DateTime)
    EndProcessing = mapped_column(DateTime)
    SecondsInPreviousAttempts = mapped_column(Integer)
    RetryNumber = mapped_column(Integer)
    SpecificContent = mapped_column(JSON)
    CreationTime = mapped_column(DateTime)
    Progress = mapped_column(String)
    RowVersion = mapped_column(String)
    ProcessingException = mapped_column(JSON)  # TODO expand these columns?
    SpecificContent = mapped_column(JSON)
    Output = mapped_column(JSON)
    Analytics = mapped_column(JSON)
    # Refs
    Events = relationship("QueueItemEvent", back_populates="QueueItems")
    Folder = relationship("Folder", back_populates="QueueItems")
    QueueDefinition = relationship("QueueDefinitions", back_populates="QueueItems")


class QueueItemEvent(Base):
    __tablename__ = "uipath_queueitemevents"
    Id = mapped_column(Integer, primary_key=True, index=True)
    QueueItemId = mapped_column(ForeignKey("uipath_queueitems.Id"))
    UserId = mapped_column(Integer)
    Timestamp = mapped_column(DateTime)
    Action = mapped_column(String)
    Data = mapped_column(String)
    UserName = mapped_column(String)
    Status = mapped_column(String)
    ReviewStatus = mapped_column(String)
    ReviewerUserId = mapped_column(Integer)
    ReviewerUserName = mapped_column(String)
    ExternalClientId = mapped_column(Integer)
    # refs
    QueueItems = relationship("QueueItem", back_populates="Events")


class Job(Base):
    __tablename__ = "uipath_jobs"
    Id = mapped_column(Integer, primary_key=True, index=True)
    Key = mapped_column(UUID)
    StartingScheduleId = mapped_column(Integer)
    OrganizationUnitId = mapped_column(ForeignKey("uipath_folders.Id"))
    PersistenceId = mapped_column(Integer)
    StartTime = mapped_column(DateTime)
    EndTime = mapped_column(DateTime)
    State = mapped_column(String)
    JobPriority = mapped_column(String)
    ResourceOverwrites = mapped_column(String)
    Source = mapped_column(String)
    SourceType = mapped_column(String)
    Info = mapped_column(String)
    CreationTime = mapped_column(DateTime)
    ReleaseName = mapped_column(String)
    InputArguments = mapped_column(JSON)
    OutputArguments = mapped_column(JSON)
    HostMachineName = mapped_column(String)
    StopStrategy = mapped_column(String)
    Reference = mapped_column(String)
    LocalSystemAccount = mapped_column(String)
    OrchestratorUserIdentity = mapped_column(String)
    MaxExpectedRunningTimeSeconds = mapped_column(Integer)
    # Refs
    # Establish the relationship with Folder
    Folder = relationship("Folder", back_populates="Jobs")


class Sessions(Base):
    __tablename__ = "uipath_sessions"
    SessionId = mapped_column(Integer, primary_key=True, index=True)
    MachineId = mapped_column(Integer)  # TODO Relationship and expand
    MachineName = mapped_column(String)
    HostMachineName = mapped_column(String)
    RuntimeType = mapped_column(String)
    Status = mapped_column(String)
    IsUnresponsive = mapped_column(Boolean)
    Runtimes = mapped_column(Integer)
    UsedRuntimes = mapped_column(Integer)
    ServiceUserName = mapped_column(String)
    Platform = mapped_column(String)
