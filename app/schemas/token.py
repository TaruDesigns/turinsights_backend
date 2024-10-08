from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import ConfigDict, BaseModel, Field


class RefreshTokenBase(BaseModel):
    token: str
    is_valid: bool = True


class RefreshTokenCreate(RefreshTokenBase):
    pass


class RefreshTokenUpdate(RefreshTokenBase):
    is_valid: bool = Field(..., description="Deliberately disable a refresh token.")  # type: ignore


class RefreshToken(RefreshTokenUpdate):
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[UUID] = None
    refresh: Optional[bool] = False
    totp: Optional[bool] = False


class MagicTokenPayload(BaseModel):
    sub: Optional[UUID] = None
    fingerprint: Optional[UUID] = None


class WebToken(BaseModel):
    claim: str


# Schemas for the UIPath Authentication


class UIPathTokenResponse(BaseModel):
    access_token: str
    expires_in: int
    token_type: str
    scope: str
    expires_at: datetime


class UIPathTokenBearer(BaseModel):
    access_token: str
