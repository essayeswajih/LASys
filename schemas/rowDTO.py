from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class RowDTO(BaseModel):
    ip: Optional[str] = None
    dateTime: Optional[str] = None
    method: Optional[str] = None
    url: Optional[str] = None
    status: Optional[int] = None
    referer: Optional[str] = None
    user_agent: Optional[str] = None
    log_id: Optional[int] = None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
