from sqlalchemy.orm import Session
from app.database.connection import SessionLocal
from app.models.user import User
from app.models.room import Room
from app.models.device import Device
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed_data():
    db = SessionLocal()
    try:
        # Check if admin exists
        admin = db.query(User).filter(User.email == "admin@smartclass.local").first()
        if not admin:
            admin = User(
                email="admin@smartclass.local",
                password_hash=pwd_context.hash("Admin@123"),
                role="admin"
            )
            db.add(admin)
        
        # Check if room exists
        room = db.query(Room).filter(Room.room_code == "ROOM_01").first()
        if not room:
            room = Room(
                room_code="ROOM_01",
                room_name="Phong hoc AIoT",
                location="Tang 1",
                temperature_threshold=30.0,
                occupancy_limit=50
            )
            db.add(room)
            
        # Check if device exists
        device = db.query(Device).filter(Device.device_id == "ESP32_ROOM_01").first()
        if not device:
            device = Device(
                device_id="ESP32_ROOM_01",
                room_id="ROOM_01",
                device_name="Thiet bi mo phong ESP32",
                device_type="Simulator"
            )
            db.add(device)
            
        db.commit()
        print("Database seeded successfully.")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
