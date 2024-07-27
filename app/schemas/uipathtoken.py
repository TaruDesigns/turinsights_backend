from datetime import datetime

from pydantic import BaseModel


class UIPathTokenResponse(BaseModel):
    access_token: str
    expires_in: int
    token_type: str
    scope: str
    expires_at: datetime


class UIPathTokenBearer(BaseModel):
    access_token: str
