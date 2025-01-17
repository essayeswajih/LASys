from typing import List, Optional
from pydantic import BaseModel
from schemas.rowDTO import RowDTO 

class LogDTO(BaseModel):
    id: int 
    rows: List[RowDTO] = []
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
        from_attributes = True
        arbitrary_types_allowed = True