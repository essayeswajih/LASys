from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class RowDTO(BaseModel):
    id: Optional[int] = None
    ip: Optional[str] = None
    url: Optional[str] = None
    timestamp: Optional[str] = None
    method: Optional[str] = None
    status: Optional[int] = None
    response_size: Optional[int] = None
    referer: Optional[str] = None
    user_agent: Optional[str] = None
    protocol: Optional[str] = None
    src_port: Optional[int] = None
    dest_port: Optional[int] = None
    message: Optional[str] = None
    level: Optional[str] = None
    component: Optional[str] = None
    log_id: Optional[int] = None
    remote_logname: Optional[str] = None
    user: Optional[str] = None
    request: Optional[str] = None
    pid_tid: Optional[str] = None

    class Config:
        from_attributes = True  # Allow SQLAlchemy models to be converted to Pydantic models
        arbitrary_types_allowed = True
        
class RowCreate(BaseModel):
    ip: Optional[str] = None
    timestamp: Optional[str] = None
    method: Optional[str] = None
    url: Optional[str] = None
    status: Optional[int] = None
    response_size: Optional[int] = None
    referer: Optional[str] = None
    user_agent: Optional[str] = None
    protocol : Optional[str] = None
    src_port : Optional[int] = None
    dest_port : Optional[int] = None
    message : Optional[str] = None
    level : Optional[str] = None
    component : Optional[str] = None
    remote_logname: Optional[str] = None
    user: Optional[str] = None
    log_id: Optional[int] = None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

