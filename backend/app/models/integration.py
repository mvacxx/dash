from datetime import datetime
from enum import Enum
from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship

from .base import Base


class IntegrationType(str, Enum):
    FACEBOOK = "facebook_ads"
    ADSENSE = "google_adsense"


class IntegrationAccount(Base):
    __tablename__ = "integration_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(SQLEnum(IntegrationType), nullable=False)
    credentials = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", backref="integrations")
