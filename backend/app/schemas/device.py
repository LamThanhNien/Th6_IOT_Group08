from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DeviceBase(BaseModel):
    device_id: str
    room_id: str
    device_name: Optional[str] = None
    device_type: Optional[str] = None

class DeviceCreate(DeviceBase):
    pass

class DeviceUpdate(DeviceBase):
    device_id: Optional[str] = None
    room_id: Optional[str] = None

class DeviceResponse(DeviceBase):
    id: int
    online: bool
    last_seen: Optional[datetime] = None
    fan_status: bool
    led_status: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

