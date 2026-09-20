import logging
import asyncio
from datetime import datetime
from app.database.connection import SessionLocal
from app.models.telemetry import Telemetry
from app.models.vision_detection import VisionDetection
from app.models.device import Device
from app.models.command import Command
from app.websocket.manager import manager
from app.services.rules import evaluate_rules

logger = logging.getLogger(__name__)

main_loop = None

def process_mqtt_message(topic: str, payload: dict):
    db = SessionLocal()
    try:
        parts = topic.split("/")
        ws_msg = {"topic": topic, "payload": payload}
        room_id = payload.get("roomId")
        
        if len(parts) >= 3 and parts[2] == "devices" and parts[-1] == "telemetry":
            telemetry = Telemetry(
                device_id=payload.get("deviceId"),
                room_id=room_id,
                temperature=payload.get("temperature"),
                humidity=payload.get("humidity"),
                timestamp=datetime.utcnow()
            )
            db.add(telemetry)
            
            device = db.query(Device).filter(Device.device_id == payload.get("deviceId")).first()
            if device:
                device.last_seen = datetime.utcnow()
                device.online = True
                
            db.commit()
            logger.info(f"Saved telemetry for {payload.get('deviceId')}")
            
        elif len(parts) == 3 and parts[-1] == "vision":
            vision = VisionDetection(
                camera_id=payload.get("cameraId"),
                room_id=room_id,
                person_count=payload.get("personCount", 0),
                confidence_average=payload.get("confidenceAverage", 0.0),
                camera_status=payload.get("cameraStatus", "online"),
                timestamp=datetime.utcnow()
            )
            db.add(vision)
            db.commit()
            logger.info(f"Saved vision for {payload.get('cameraId')}")
            
        elif len(parts) >= 3 and parts[2] == "devices" and parts[-1] == "status":
            cmd_id = payload.get("commandId")
            if cmd_id:
                command = db.query(Command).filter(Command.command_id == cmd_id).first()
                if command:
                    command.status = payload.get("status", "success")
                    command.responded_at = datetime.utcnow()
                    db.commit()
            
            device = db.query(Device).filter(Device.device_id == payload.get("deviceId")).first()
            if device:
                if "fan" in payload:
                    device.fan_status = payload["fan"]
                if "led" in payload:
                    device.led_status = payload["led"]
                device.last_seen = datetime.utcnow()
                device.online = True
                db.commit()
            logger.info(f"Processed status for {payload.get('deviceId')}")
            
        if room_id:
            evaluate_rules(db, room_id)
            
        # Broadcast via WebSocket
        if main_loop and manager.active_connections:
            asyncio.run_coroutine_threadsafe(manager.broadcast(ws_msg), main_loop)
            
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        db.rollback()
    finally:
        db.close()

