# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.models.orchestratorapi import Folder  # noqa
from app.models.token import Token  # noqa
from app.models.uipathtoken import UIPathToken  # noqa
from app.models.user import User  # noqa
