from typing import List, Optional
from pydantic import BaseModel
from models.rowEntity import Row
class LogDTO(BaseModel):
    id: int
    rows: Optional[List[Row]] = []
    log_of: Optional[str] = None
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    class Config:
        from_attributes = True