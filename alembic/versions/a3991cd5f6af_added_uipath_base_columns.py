"""Added UIPath Base Columns

Revision ID: a3991cd5f6af
Revises: 8188d671489a
Create Date: 2023-07-29 13:07:29.399227

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a3991cd5f6af"
down_revision = "8188d671489a"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "uipath_folders",
        sa.Column("Id", sa.Integer(), nullable=False),
        sa.Column("Key", sa.UUID(), nullable=True),
        sa.Column("DisplayName", sa.String(), nullable=True),
        sa.Column("FullyQualifiedName", sa.String(), nullable=True),
        sa.Column("Description", sa.String(), nullable=True),
        sa.Column("FolderType", sa.String(), nullable=True),
        sa.Column("ParentId", sa.Integer(), nullable=True),
        sa.Column("ParentKey", sa.UUID(), nullable=True),
        sa.PrimaryKeyConstraint("Id"),
    )
    op.create_index(
        op.f("ix_uipath_folders_DisplayName"),
        "uipath_folders",
        ["DisplayName"],
        unique=False,
    )
    op.create_index(
        op.f("ix_uipath_folders_Id"), "uipath_folders", ["Id"], unique=False
    )
    op.create_table(
        "uipath_jobs",
        sa.Column("Id", sa.Integer(), nullable=False),
        sa.Column("Key", sa.UUID(), nullable=True),
        sa.Column("StartingScheduleId", sa.Integer(), nullable=True),
        sa.Column("OrganizationUnitId", sa.Integer(), nullable=True),
        sa.Column("PersistenceId", sa.Integer(), nullable=True),
        sa.Column("StartTime", sa.DateTime(), nullable=True),
        sa.Column("EndTime", sa.DateTime(), nullable=True),
        sa.Column("State", sa.String(), nullable=True),
        sa.Column("JobPriority", sa.String(), nullable=True),
        sa.Column("ResourceOverwrites", sa.String(), nullable=True),
        sa.Column("Source", sa.String(), nullable=True),
        sa.Column("SourceType", sa.String(), nullable=True),
        sa.Column("Info", sa.String(), nullable=True),
        sa.Column("CreationTime", sa.DateTime(), nullable=True),
        sa.Column("ReleaseName", sa.String(), nullable=True),
        sa.Column("InputArguments", sa.JSON(), nullable=True),
        sa.Column("OutputArguments", sa.JSON(), nullable=True),
        sa.Column("HostMachineName", sa.String(), nullable=True),
        sa.Column("StopStrategy", sa.String(), nullable=True),
        sa.Column("Reference", sa.String(), nullable=True),
        sa.Column("LocalSystemAccount", sa.String(), nullable=True),
        sa.Column("OrchestratorUserIdentity", sa.String(), nullable=True),
        sa.Column("MaxExpectedRunningTimeSeconds", sa.Integer(), nullable=True),
        sa.Column("OrganizationUnitFullyQualifiedName", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("Id"),
    )
    op.create_index(op.f("ix_uipath_jobs_Id"), "uipath_jobs", ["Id"], unique=False)
    op.create_table(
        "uipath_processes",
        sa.Column("Key", sa.UUID(), nullable=False),
        sa.Column("Id", sa.Integer(), nullable=True),
        sa.Column("OrganizationUnitId", sa.Integer(), nullable=True),
        sa.Column("Name", sa.String(), nullable=True),
        sa.Column("JobPriority", sa.String(), nullable=True),
        sa.Column("Arguments", sa.JSON(), nullable=True),
        sa.Column("OrganizationUnitFullyQualifiedName", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("Key"),
    )
    op.create_index(
        op.f("ix_uipath_processes_Key"), "uipath_processes", ["Key"], unique=False
    )
    op.create_table(
        "uipath_queuedefinitions",
        sa.Column("Id", sa.Integer(), nullable=False),
        sa.Column("Key", sa.UUID(), nullable=True),
        sa.Column("OrganizationUnitId", sa.Integer(), nullable=True),
        sa.Column("ReleaseId", sa.Integer(), nullable=True),
        sa.Column("Name", sa.String(), nullable=True),
        sa.Column("CreationTime", sa.DateTime(), nullable=True),
        sa.Column("Description", sa.String(), nullable=True),
        sa.Column("MaxNumberOfRetires", sa.Integer(), nullable=True),
        sa.Column("AcceptAutomaticallyRetry", sa.Boolean(), nullable=True),
        sa.Column("EnforceUniqueReference", sa.Boolean(), nullable=True),
        sa.Column("Encrypted", sa.Boolean(), nullable=True),
        sa.Column("SpecificDataJsonSchema", sa.String(), nullable=True),
        sa.Column("OutputDataJsonSchema", sa.String(), nullable=True),
        sa.Column("AnalyticsDataJsonSchema", sa.String(), nullable=True),
        sa.Column("ProcessScheduleId", sa.Integer(), nullable=True),
        sa.Column("SlaInMinutes", sa.Integer(), nullable=True),
        sa.Column("RiskSlaInMinutes", sa.Integer(), nullable=True),
        sa.Column("IsProcessInCurrentFolder", sa.Boolean(), nullable=True),
        sa.Column("FoldersCount", sa.Integer(), nullable=True),
        sa.Column("Tags", sa.JSON(), nullable=True),
        sa.Column("OrganizationUnitFullyQualifiedName", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("Id"),
    )
    op.create_index(
        op.f("ix_uipath_queuedefinitions_Id"),
        "uipath_queuedefinitions",
        ["Id"],
        unique=False,
    )
    op.create_table(
        "uipath_queueitems",
        sa.Column("Id", sa.Integer(), nullable=False),
        sa.Column("QueueDefinitionId", sa.Integer(), nullable=True),
        sa.Column("ReviewerUserId", sa.Integer(), nullable=True),
        sa.Column("AncestorId", sa.Integer(), nullable=True),
        sa.Column("OrganizationUnitId", sa.Integer(), nullable=True),
        sa.Column("Status", sa.String(), nullable=True),
        sa.Column("ReviewStatus", sa.String(), nullable=True),
        sa.Column("Key", sa.UUID(), nullable=True),
        sa.Column("Reference", sa.String(), nullable=True),
        sa.Column("ProcessingExceptionType", sa.String(), nullable=True),
        sa.Column("DueDate", sa.DateTime(), nullable=True),
        sa.Column("RiskSlaDate", sa.DateTime(), nullable=True),
        sa.Column("Priority", sa.String(), nullable=True),
        sa.Column("DeferDate", sa.DateTime(), nullable=True),
        sa.Column("StartProcessing", sa.DateTime(), nullable=True),
        sa.Column("EndProcessing", sa.DateTime(), nullable=True),
        sa.Column("SecondsInPreviousAttempts", sa.Integer(), nullable=True),
        sa.Column("RetryNumber", sa.Integer(), nullable=True),
        sa.Column("SpecificContent", sa.JSON(), nullable=True),
        sa.Column("CreationTime", sa.DateTime(), nullable=True),
        sa.Column("Progress", sa.String(), nullable=True),
        sa.Column("RowVersion", sa.String(), nullable=True),
        sa.Column("ProcessingException", sa.JSON(), nullable=True),
        sa.Column("Output", sa.JSON(), nullable=True),
        sa.Column("Analytics", sa.JSON(), nullable=True),
        sa.Column("QueueDefinitionName", sa.String(), nullable=True),
        sa.Column("OrganizationUnitFullyQualifiedName", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("Id"),
    )
    op.create_index(
        op.f("ix_uipath_queueitems_Id"), "uipath_queueitems", ["Id"], unique=False
    )
    op.create_table(
        "uipath_sessions",
        sa.Column("SessionId", sa.Integer(), nullable=False),
        sa.Column("MachineId", sa.Integer(), nullable=True),
        sa.Column("MachineName", sa.String(), nullable=True),
        sa.Column("HostMachineName", sa.String(), nullable=True),
        sa.Column("RuntimeType", sa.String(), nullable=True),
        sa.Column("Status", sa.String(), nullable=True),
        sa.Column("IsUnresponsive", sa.Boolean(), nullable=True),
        sa.Column("Runtimes", sa.Integer(), nullable=True),
        sa.Column("UsedRuntimes", sa.Integer(), nullable=True),
        sa.Column("ServiceUserName", sa.String(), nullable=True),
        sa.Column("Platform", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("SessionId"),
    )
    op.create_index(
        op.f("ix_uipath_sessions_SessionId"),
        "uipath_sessions",
        ["SessionId"],
        unique=False,
    )
    op.create_table(
        "uipath_token",
        sa.Column("access_token", sa.String(), nullable=False),
        sa.Column("expires_in", sa.Integer(), nullable=False),
        sa.Column("token_type", sa.String(), nullable=False),
        sa.Column("scope", sa.String(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("access_token"),
    )
    op.create_index(
        op.f("ix_uipath_token_access_token"),
        "uipath_token",
        ["access_token"],
        unique=False,
    )
    op.create_table(
        "uipath_queueitemevents",
        sa.Column("Id", sa.Integer(), nullable=False),
        sa.Column("QueueItemId", sa.Integer(), nullable=True),
        sa.Column("UserId", sa.Integer(), nullable=True),
        sa.Column("Timestamp", sa.DateTime(), nullable=True),
        sa.Column("Action", sa.String(), nullable=True),
        sa.Column("Data", sa.String(), nullable=True),
        sa.Column("UserName", sa.String(), nullable=True),
        sa.Column("Status", sa.String(), nullable=True),
        sa.Column("ReviewStatus", sa.String(), nullable=True),
        sa.Column("ReviewerUserId", sa.Integer(), nullable=True),
        sa.Column("ReviewerUserName", sa.String(), nullable=True),
        sa.Column("ExternalClientId", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["QueueItemId"],
            ["uipath_queueitems.Id"],
        ),
        sa.PrimaryKeyConstraint("Id"),
    )
    op.create_index(
        op.f("ix_uipath_queueitemevents_Id"),
        "uipath_queueitemevents",
        ["Id"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        op.f("ix_uipath_queueitemevents_Id"), table_name="uipath_queueitemevents"
    )
    op.drop_table("uipath_queueitemevents")
    op.drop_index(op.f("ix_uipath_token_access_token"), table_name="uipath_token")
    op.drop_table("uipath_token")
    op.drop_index(op.f("ix_uipath_sessions_SessionId"), table_name="uipath_sessions")
    op.drop_table("uipath_sessions")
    op.drop_index(op.f("ix_uipath_queueitems_Id"), table_name="uipath_queueitems")
    op.drop_table("uipath_queueitems")
    op.drop_index(
        op.f("ix_uipath_queuedefinitions_Id"), table_name="uipath_queuedefinitions"
    )
    op.drop_table("uipath_queuedefinitions")
    op.drop_index(op.f("ix_uipath_processes_Key"), table_name="uipath_processes")
    op.drop_table("uipath_processes")
    op.drop_index(op.f("ix_uipath_jobs_Id"), table_name="uipath_jobs")
    op.drop_table("uipath_jobs")
    op.drop_index(op.f("ix_uipath_folders_Id"), table_name="uipath_folders")
    op.drop_index(op.f("ix_uipath_folders_DisplayName"), table_name="uipath_folders")
    op.drop_table("uipath_folders")
    # ### end Alembic commands ###
