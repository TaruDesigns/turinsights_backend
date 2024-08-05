from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class UIPathToken(Base):
    __tablename__ = "uipath_token"  # type: ignore
    access_token: Mapped[str] = mapped_column(primary_key=True, index=True)
    expires_in: Mapped[int] = mapped_column(default=3600)
    token_type: Mapped[str] = mapped_column(default="Bearer")
    scope: Mapped[str] = mapped_column()
    expires_at: Mapped[datetime] = mapped_column(default=datetime.now)

    def is_valid(self):
        if self.expires_at is not None:
            return datetime.now() <= self.expires_at
        return False
