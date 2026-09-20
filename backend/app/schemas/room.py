from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RoomBase(BaseModel):
    room_code: str
    room_name: str
    location: Optional[str] = None
    temperature_threshold: Optional[float] = 30.0
    occupancy_limit: Optional[int] = 50

class RoomCreate(RoomBase):
    pass

class RoomUpdate(RoomBase):
    room_code: Optional[str] = None
    room_name: Optional[str] = None

class RoomResponse(RoomBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

