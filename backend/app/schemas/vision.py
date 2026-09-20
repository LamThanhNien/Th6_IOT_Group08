from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class VisionDetectionResponse(BaseModel):
    id: int
    camera_id: str
    room_id: str
    person_count: int
    confidence_average: float
    camera_status: str
    timestamp: datetime
    snapshot_path: Optional[str] = None
    
    class Config:
        from_attributes = True

