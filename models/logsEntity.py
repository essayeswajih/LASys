from sqlalchemy import Integer, String, Column
from sqlalchemy.orm import relationship
from db.database import Base

class Log(Base):
    __tablename__ = "log"
    
    id = Column(Integer, primary_key=True, index=True)
    log_of = Column(String)  # Fixed column definition
    file_name = Column(String)  # Fixed column definition
    file_type = Column(String)  # Fixed column definition
    
    rows = relationship("Row", back_populates="owner")
