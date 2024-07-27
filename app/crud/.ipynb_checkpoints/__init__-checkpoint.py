from .crud_user import user
from .crud_token import token
from .crud_uipathtoken import uipath_token
from .crud_orchestratorapi import (
    folder as uip_folder,
    job as uip_job,
    process as uip_process,
    queue_item as uip_queue_item,
    queue_item_event as uip_queue_item_event,
)


# For a new basic set of CRUD operations you could just do

# from .base import CRUDBase
# from app.models.item import Item
# from app.schemas.item import ItemCreate, ItemUpdate

# item = CRUDBase[Item, ItemCreate, ItemUpdate](Item)
