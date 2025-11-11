from datetime import datetime
from typing import Any, Dict, Literal, Optional
from pydantic import BaseModel, Field


class BaseIntegration(BaseModel):
    account_id: str = Field(..., description="Identifier of the ad account")
    access_token: str = Field(..., description="OAuth access token")


class FacebookIntegrationCreate(BaseIntegration):
    api_version: Optional[str] = Field(
        default=None, description="Graph API version override (default v18.0)"
    )
    business_id: Optional[str] = Field(
        default=None, description="Optional business identifier to scope the insights"
    )


class AdSenseIntegrationCreate(BaseModel):
    account_id: str = Field(..., description="Resource name of the AdSense account")
    access_token: str = Field(..., description="OAuth access token with adsense scope")
    refresh_token: str = Field(..., description="OAuth refresh token with adsense scope")
    client_id: str = Field(..., description="Google OAuth client id")
    client_secret: str = Field(..., description="Google OAuth client secret")
    token_expiry: Optional[datetime] = Field(
        default=None,
        description="Expiration datetime of the provided access token (UTC)",
    )
    expires_in: Optional[int] = Field(
        default=None,
        description="Seconds until the provided access token expires",
    )


class FacebookIntegrationUpdate(BaseModel):
    account_id: Optional[str] = Field(default=None, description="Identifier of the ad account")
    access_token: Optional[str] = Field(default=None, description="OAuth access token")
    business_id: Optional[str] = Field(default=None, description="Optional business identifier")
    api_version: Optional[str] = Field(default=None, description="Graph API version override")


class AdSenseIntegrationUpdate(BaseModel):
    account_id: Optional[str] = Field(default=None, description="Resource name of the AdSense account")
    access_token: Optional[str] = Field(default=None, description="OAuth access token with adsense scope")
    refresh_token: Optional[str] = Field(default=None, description="OAuth refresh token with adsense scope")
    client_id: Optional[str] = Field(default=None, description="Google OAuth client id")
    client_secret: Optional[str] = Field(default=None, description="Google OAuth client secret")
    token_expiry: Optional[datetime] = Field(
        default=None,
        description="Expiration datetime of the provided access token (UTC)",
    )
    expires_in: Optional[int] = Field(
        default=None,
        description="Seconds until the provided access token expires",
    )


class IntegrationRead(BaseModel):
    id: int
    type: Literal["facebook_ads", "google_adsense"]
    credentials: Dict[str, Any]
    created_at: datetime

    class Config:
        orm_mode = True
