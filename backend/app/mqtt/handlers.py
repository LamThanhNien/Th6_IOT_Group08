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
        
        is_telemetry = (len(parts) >= 3 and parts[2] == "devices" and parts[-1] == "telemetry") or (len(parts) == 3 and parts[0] == "device" and parts[2] == "telemetry")
        is_vision = (len(parts) == 3 and parts[-1] == "vision")
        is_status = (len(parts) >= 3 and parts[2] == "devices" and parts[-1] == "status") or (len(parts) >= 3 and parts[0] == "device" and parts[-1] in ("status", "ack"))

        if not room_id:
            room_id = "ROOM_01"

        if is_telemetry:
            raw_dev = payload.get("deviceId") or "ESP32_ROOM_01"
            target_device_id = "ESP32_ROOM_01" if raw_dev in ("esp32-001", "ESP32_ROOM_01") else raw_dev

            telemetry = Telemetry(
                device_id=target_device_id,
                room_id=room_id,
                temperature=payload.get("temperature"),
                humidity=payload.get("humidity"),
                timestamp=datetime.utcnow()
            )
            db.add(telemetry)
            
            device = db.query(Device).filter(Device.device_id == target_device_id).first()
            if device:
                device.last_seen = datetime.utcnow()
                device.online = True
                if "led" in payload:
                    device.led_status = bool(payload["led"])
                
            db.commit()
            logger.info(f"Saved telemetry for {target_device_id}: T={payload.get('temperature')}, H={payload.get('humidity')}")
            
        elif is_vision:
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
            
        elif is_status:
            cmd_id = payload.get("commandId")
            if cmd_id:
                command = db.query(Command).filter(Command.command_id == cmd_id).first()
                if command:
                    command.status = payload.get("status", "success")
                    command.responded_at = datetime.utcnow()
                    db.commit()
            
            raw_dev = payload.get("deviceId") or "ESP32_ROOM_01"
            target_device_id = "ESP32_ROOM_01" if raw_dev in ("esp32-001", "ESP32_ROOM_01") else raw_dev

            device = db.query(Device).filter(Device.device_id == target_device_id).first()
            if device:
                if "fan" in payload:
                    device.fan_status = bool(payload["fan"])
                if "led" in payload:
                    device.led_status = bool(payload["led"])
                device.last_seen = datetime.utcnow()
                device.online = True
                db.commit()
            logger.info(f"Processed status for {target_device_id}")
            
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

