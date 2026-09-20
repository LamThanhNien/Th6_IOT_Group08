from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
from app.database.connection import get_db
from app.models.device import Device
from app.models.room import Room
from app.schemas.device import DeviceCreate, DeviceUpdate, DeviceResponse
from app.services.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[DeviceResponse])
def get_devices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(Device).offset(skip).limit(limit).all()

@router.post("/register", response_model=DeviceResponse)
def register_device(device: DeviceCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    room = db.query(Room).filter(Room.room_code == device.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
        
    db_device = db.query(Device).filter(Device.device_id == device.device_id).first()
    if db_device:
        raise HTTPException(status_code=409, detail="Device ID already registered")
        
    db_device = Device(**device.model_dump())
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device

