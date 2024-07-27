from typing import List, Optional

from fastapi import Query
from pydantic import BaseModel


class ODataForm(BaseModel):
    filter: Optional[str] = Query()
    select: Optional[str] = Query()
    top: Optional[int] = Query()
    skip: Optional[int] = Query()


class UIPFetchPostBody(BaseModel):
    cruddb: bool = False
    upsert: bool = False
    fulldata: bool = False
    filter: Optional[str]
    folderlist: Optional[List[int]]
