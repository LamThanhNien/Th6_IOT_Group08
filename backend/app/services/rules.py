from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.room import Room
from app.models.device import Device
from app.models.telemetry import Telemetry
from app.models.vision_detection import VisionDetection
from app.models.alert import Alert
import logging

logger = logging.getLogger(__name__)

def evaluate_rules(db: Session, room_id: str):
    room = db.query(Room).filter(Room.room_code == room_id).first()
    if not room:
        return

    # Get latest vision and telemetry
    latest_vision = db.query(VisionDetection).filter(VisionDetection.room_id == room_id).order_by(VisionDetection.timestamp.desc()).first()
    latest_telemetry = db.query(Telemetry).filter(Telemetry.room_id == room_id).order_by(Telemetry.timestamp.desc()).first()
    devices = db.query(Device).filter(Device.room_id == room_id).all()
    
    person_count = latest_vision.person_count if latest_vision else 0
    
    # Rule 1: High temperature when people are present
    if person_count > 0 and latest_telemetry and latest_telemetry.temperature >= room.temperature_threshold:
        create_alert(db, room_id, latest_telemetry.device_id, "HIGH_TEMP", "Warning", "Nhiệt độ cao", f"Nhiệt độ phòng là {latest_telemetry.temperature}°C vượt ngưỡng {room.temperature_threshold}°C")
        
    # Rule 2: Overcrowded
    if person_count > room.occupancy_limit:
        create_alert(db, room_id, latest_vision.camera_id if latest_vision else None, "OVERCROWDED", "Warning", "Quá tải số người", f"Số người hiện tại {person_count} vượt ngưỡng {room.occupancy_limit}")
        
    # Rule 3: No people but devices are on (check for 2 minutes)
    if person_count == 0:
        two_mins_ago = datetime.utcnow() - timedelta(minutes=2)
        recent_visions = db.query(VisionDetection).filter(VisionDetection.room_id == room_id, VisionDetection.timestamp >= two_mins_ago).all()
        # If all recent visions have 0 people, and we have enough history (at least 1 record 2 mins ago, but simplified here)
        if all(v.person_count == 0 for v in recent_visions):
            for device in devices:
                if device.fan_status or device.led_status:
                    create_alert(db, room_id, device.device_id, "WASTE_ENERGY", "Info", "Lãng phí năng lượng", f"Phòng không có người nhưng thiết bị {device.device_name} đang bật")

    # Rule 4: Offline devices
    offline_threshold = datetime.utcnow() - timedelta(seconds=30)
    for device in devices:
        if device.last_seen and device.last_seen < offline_threshold and device.online:
            device.online = False
            db.commit()
            create_alert(db, room_id, device.device_id, "DEVICE_OFFLINE", "Error", "Mất kết nối", f"Thiết bị {device.device_name} mất kết nối")

def create_alert(db: Session, room_id, source_id, alert_type, severity, title, message):
    # Check if there is an active unacknowledged alert of the same type for the source
    existing = db.query(Alert).filter(Alert.room_id == room_id, Alert.source_id == source_id, Alert.alert_type == alert_type, Alert.acknowledged == False).first()
    if not existing:
        alert = Alert(
            room_id=room_id,
            source_id=source_id,
            alert_type=alert_type,
            severity=severity,
            title=title,
            message=message,
            created_at=datetime.utcnow()
        )
        db.add(alert)
        db.commit()
        logger.info(f"Created alert: {title}")
