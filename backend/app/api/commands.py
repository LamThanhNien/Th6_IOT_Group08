from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime
from app.database.connection import get_db
from app.models.command import Command
from app.models.device import Device
from app.schemas.command import CommandCreate, CommandResponse
from app.services.auth import get_current_user
from app.mqtt.client import mqtt_client

router = APIRouter()

@router.post("/", response_model=CommandResponse)
@router.post("/{device_id}", response_model=CommandResponse)
def send_command(command: CommandCreate, device_id: str = None, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    target_device_id = device_id or command.device_id
    if not target_device_id:
        raise HTTPException(status_code=400, detail="Device ID is required")
        
    device = db.query(Device).filter(Device.device_id == target_device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    command_id = str(uuid.uuid4())
    db_command = Command(
        command_id=command_id,
        device_id=target_device_id,
        action=command.action,
        value=str(command.value) if command.value is not None else None,
        status="pending",
        issued_by=current_user.email,
        timestamp=datetime.utcnow()
    )
    db.add(db_command)
    db.commit()
    db.refresh(db_command)
    
    # Publish to MQTT
    topic = f"rooms/{device.room_id}/devices/{target_device_id}/commands"
    payload = {
        "commandId": command_id,
        "deviceId": target_device_id,
        "action": command.action,
        "value": command.value,
        "issuedBy": current_user.email,
        "timestamp": db_command.timestamp.isoformat() + "Z"
    }
    mqtt_client.publish(topic, payload)
    
    db_command.status = "published"
    db.commit()
    db.refresh(db_command)
    return db_command

@router.get("/", response_model=List[CommandResponse])
def get_commands(limit: int = 100, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(Command).order_by(Command.timestamp.desc()).limit(limit).all()

