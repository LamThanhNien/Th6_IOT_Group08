from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from datetime import datetime
from .base import Base

class Device(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, unique=True, index=True, nullable=False)
    room_id = Column(String, index=True, nullable=False)
    device_name = Column(String)
    device_type = Column(String)
    firmware_version = Column(String)
    api_key_hash = Column(String)
    online = Column(Boolean, default=False)
    last_seen = Column(DateTime, nullable=True)
    fan_status = Column(Boolean, default=False)
    led_status = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

