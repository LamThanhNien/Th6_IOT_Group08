from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AlertResponse(BaseModel):
    id: int
    room_id: str
    source_id: Optional[str] = None
    alert_type: str
    severity: str
    title: str
    message: str
    acknowledged: bool
    created_at: datetime
    acknowledged_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

