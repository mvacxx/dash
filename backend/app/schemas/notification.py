from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class NotificationRead(BaseModel):
    id: int
    level: Literal["info", "warning", "error"]
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        orm_mode = True
