from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud.base import CRUDBase
from app.models import UIPathToken
from app.schemas import UIPathTokenBearer, UIPathTokenResponse

default_scope = settings.UIP_SCOPE


class CRUDUIPathToken(CRUDBase[UIPathToken, UIPathTokenResponse, UIPathTokenBearer]):
    """Basic CRUD Object for uipath token

    Args:
        CRUDBase (_type_): _description_
    """

    def get(self, db: Session, *, scope=default_scope) -> str:
        # TODO implement scope: filter(UIPathToken.is_valid(), UIPathToken.scope.like('%OR%')
        return (
            db.query(UIPathToken)
            .filter(UIPathToken.is_valid(UIPathToken))
            .first()
            .access_token  # type: ignore
        )

    def remove_expired(self, db: Session):
        # Get the current time
        now = datetime.now(timezone.utc)
        # Using a delete statement to remove all rows where expires_at is less than the current time
        stmt = delete(self.model).where(self.model.expires_at < now)
        db.execute(stmt)
        db.commit()


uipath_token = CRUDUIPathToken(UIPathToken)
uipath_token = CRUDUIPathToken(UIPathToken)
