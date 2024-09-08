from sqlalchemy import Boolean, Integer, String, Column,DateTime, ForeignKey
from sqlalchemy.orm import relationship
from db.database import Base

class Row(Base):
    __tablename__ = "row"
    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String, index=True)
    url = Column(String)
    dateTime = Column(DateTime)
    method = Column(String)
    status = Column(Integer)
    referer = Column(String)
    user_agent = Column(String)
    log_id = Column(Integer, ForeignKey('log.id'))
    owner = relationship("Log", back_populates="rows")
