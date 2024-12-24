from sqlalchemy import Boolean, Integer, String, Column,DateTime, ForeignKey
from sqlalchemy.orm import relationship
from db.database import Base

class Row(Base):
    __tablename__ = "row"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ip = Column(String, index=True)
    url = Column(String)
    timestamp = Column(String)
    method = Column(String)
    status = Column(Integer)
    referer = Column(String)
    user_agent = Column(String)
    response_size = Column(Integer)
    
    # Additional fields for compatibility with other log types
    protocol = Column(String, nullable=True)     # Network protocol (e.g., TCP, UDP, HTTP)
    src_port = Column(Integer, nullable=True)    # Source port (for firewall/network logs)
    dest_port = Column(Integer, nullable=True)   # Destination port (for network logs)
    message = Column(String, nullable=True)      # General message field for log entries
    level = Column(String, nullable=True)        # Log level (e.g., INFO, ERROR, WARNING)
    component = Column(String, nullable=True)    # Component or service generating the log
    user = Column(String, nullable=True)
    remote_logname = Column(String, nullable=True)

    log_id = Column(Integer, ForeignKey('log.id'))
    owner = relationship("Log", back_populates="rows")
