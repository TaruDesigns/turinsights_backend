from .crud_orchestratorapi import (
    uip_folder,
    uip_job,
    uip_process,
    uip_queue_definitions,
    uip_queue_item,
    uip_queue_item_event,
    uip_session,
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
