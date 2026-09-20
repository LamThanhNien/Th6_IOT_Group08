from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from .base import Base

class VisionDetection(Base):
    __tablename__ = "vision_detections"
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(String, index=True, nullable=False)
    room_id = Column(String, index=True, nullable=False)
    person_count = Column(Integer, default=0)
    confidence_average = Column(Float, default=0.0)
    camera_status = Column(String, default="online")
    timestamp = Column(DateTime, index=True, default=datetime.utcnow)
    snapshot_path = Column(String, nullable=True)

