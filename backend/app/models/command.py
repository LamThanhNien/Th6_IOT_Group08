from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .base import Base

class Command(Base):
    __tablename__ = "commands"
    id = Column(Integer, primary_key=True, index=True)
    command_id = Column(String, unique=True, index=True, nullable=False)
    device_id = Column(String, index=True, nullable=False)
    action = Column(String, nullable=False)
    value = Column(String)
    status = Column(String, default="pending")
    issued_by = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    responded_at = Column(DateTime, nullable=True)

