from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TelemetryResponse(BaseModel):
    id: int
    device_id: str
    room_id: str
    temperature: float
    humidity: float
    timestamp: datetime
    
    class Config:
        from_attributes = True

