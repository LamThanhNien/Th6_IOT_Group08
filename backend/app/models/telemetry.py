from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from .base import Base

class Telemetry(Base):
    __tablename__ = "telemetry"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True, nullable=False)
    room_id = Column(String, index=True, nullable=False)
    temperature = Column(Float)
    humidity = Column(Float)
    timestamp = Column(DateTime, index=True, default=datetime.utcnow)

