from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud.base import CRUDBase
from app.models import UIPathToken
from app.schemas import UIPathTokenBearer, UIPathTokenResponse

default_scope = settings.UIP_SCOPE


class CRUDUIPathToken(CRUDBase[UIPathToken, UIPathTokenResponse, UIPathTokenBearer]):
    """def create(self, db: Session, *, obj_in: UIPathTokenResponse) -> UIPathToken:
    db_obj = UIPathToken(**obj_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    # Refresh configuration?
    return db_obj"""

    def get(self, db: Session, *, scope=default_scope) -> UIPathTokenBearer:
        # TODO implement scope: filter(UIPathToken.is_valid(), UIPathToken.scope.like('%OR%')
        return (
            db.query(UIPathToken)
            .filter(UIPathToken.is_valid(UIPathToken))
            .first()
            .access_token
        )


uipath_token = CRUDUIPathToken(UIPathToken)
