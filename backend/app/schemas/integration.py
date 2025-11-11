from datetime import datetime
from typing import Dict, Literal, Optional
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


class IntegrationRead(BaseModel):
    id: int
    type: Literal["facebook_ads", "google_adsense"]
    credentials: Dict[str, str]
    created_at: datetime

    class Config:
        orm_mode = True
