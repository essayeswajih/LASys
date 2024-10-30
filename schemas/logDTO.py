from typing import List, Optional
from pydantic import BaseModel
from models.rowEntity import Row
class LogDTO(BaseModel):
    id: Optional[int] = None
    rows: Optional[List[Row]] = []
    log_of: Optional[str] = None
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

class LogCreate(BaseModel):
    log_of: Optional[str] = None
    file_name: Optional[str] = None
    file_type: Optional[str] = None

    class Config:
        from_attributes = True  # Allow reading data from ORMs