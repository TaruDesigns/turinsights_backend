from .crud_item import item
from .crud_orchestratorapi import (
    folder as uip_folder,
)
from .crud_orchestratorapi import (
    job as uip_job,
)
from .crud_orchestratorapi import (
    process as uip_process,
)
from .crud_orchestratorapi import (
    queue_definitions as uip_queue_definitions,
)
from .crud_orchestratorapi import (
    queue_item as uip_queue_item,
)
from .crud_orchestratorapi import (
    queue_item_event as uip_queue_item_event,
)
from .crud_orchestratorapi import (
    session as uip_session,
)
from .crud_token import token
from .crud_tracking import tracked_process, tracked_queue, tracked_synctimes
from .crud_uipathtoken import uipath_token
from .crud_user import user

# For a new basic set of CRUD operations you could just do

# from .base import CRUDBase
# from app.models.item import Item
# from app.schemas.item import ItemCreate, ItemUpdate

# item = CRUDBase[Item, ItemCreate, ItemUpdate](Item)
