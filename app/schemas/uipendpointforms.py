from typing import List, Optional

from fastapi import Query
from pydantic import BaseModel


class ODataForm(BaseModel):
    filter: Optional[str] = Query()
    select: Optional[str] = Query()
    top: Optional[int] = Query()
    skip: Optional[int] = Query()


class UIPFetchPostBody(BaseModel):
    cruddb: bool = True
    upsert: bool = True
    fulldata: bool = False
    filter: Optional[str] = None
    folderlist: Optional[List[int]]
