"""Add TrackedProcess Model

Revision ID: 704b34356b18
Revises: 6ae2d3c4854e
Create Date: 2023-08-30 17:44:54.364041

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "704b34356b18"
down_revision = "6ae2d3c4854e"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "tracked_processes",
        sa.Column("Id", sa.Integer(), nullable=False),
        sa.Column("ProcessKey", sa.UUID(), nullable=True),
        sa.Column("Strategy", sa.String(), nullable=True),
        sa.Column("CronJob", sa.String(), nullable=True),
        sa.Column("MinRetries", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["ProcessKey"],
            ["uipath_processes.Key"],
        ),
        sa.PrimaryKeyConstraint("Id"),
    )
    op.create_index(
        op.f("ix_tracked_processes_Id"), "tracked_processes", ["Id"], unique=False
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_tracked_processes_Id"), table_name="tracked_processes")
    op.drop_table("tracked_processes")
    # ### end Alembic commands ###
