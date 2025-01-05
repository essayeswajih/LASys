from sqlalchemy import Integer, String, Column
from sqlalchemy.orm import relationship
from db.database import Base

class Log(Base):
    __tablename__ = "log"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    log_of = Column(String)
    file_name = Column(String)
    file_type = Column(String)
    rows = relationship("Row", back_populates="owner")
    