from __future__ import annotations

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import mapped_column

from app.db.base_class import Base


class ScheduleSyncTimes(Base):
    # Folder = OrganizationUnit
    __tablename__ = "schedule_synctimes"  # type:ignore
    id = mapped_column(Integer, primary_key=True, index=True, autoincrement=False)
    TimeStamp = mapped_column(DateTime)
    Description = mapped_column(String)
