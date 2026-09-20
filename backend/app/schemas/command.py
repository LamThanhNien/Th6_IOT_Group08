from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any

class CommandCreate(BaseModel):
    action: str
    value: Any = None
    device_id: Optional[str] = None
    room_id: Optional[str] = None

class CommandResponse(BaseModel):
    id: int
    command_id: str
    device_id: str
    action: str
    value: Optional[str] = None
    status: str
    issued_by: Optional[str] = None
    timestamp: datetime
    responded_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

