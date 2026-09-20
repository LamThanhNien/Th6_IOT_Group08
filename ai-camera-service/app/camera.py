import cv2
import threading
import time
import os
import json
import logging
from datetime import datetime
import torch
from ultralytics import YOLO
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Limit CPU threads for PyTorch to avoid CPU starvation
torch.set_num_threads(2)

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")
ROOM_ID = os.getenv("ROOM_ID", "ROOM_01")
CAMERA_ID = os.getenv("CAMERA_ID", "CAM_ROOM_01")
CAMERA_INDEX = int(os.getenv("CAMERA_INDEX", 0))
YOLO_MODEL = os.getenv("YOLO_MODEL", "yolov8n.pt")
YOLO_CONFIDENCE = float(os.getenv("YOLO_CONFIDENCE", 0.5))

class CameraService:
    def __init__(self):
        self.cap = None
        self.model = YOLO(YOLO_MODEL)
        self.running = False
        self.capture_thread = None
        self.ai_thread = None
        self.lock = threading.Lock()
        
        self.raw_frame = None
        self.latest_frame = None
        self.latest_boxes = []
        self.person_count = 0
        
        self.mqtt_client = mqtt.Client(client_id=CAMERA_ID)
        if MQTT_USERNAME:
            self.mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
            
    def start(self):
        if self.running:
            return True
            
        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        if not self.cap.isOpened():
            logger.error("Failed to open camera")
            return False
            
        # Set buffer size to 1 to eliminate frame accumulation latency
        try:
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        except Exception:
            pass
            
        try:
            self.mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)
            self.mqtt_client.loop_start()
        except Exception as e:
            logger.error(f"MQTT connect error: {e}")
            
        self.running = True
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.ai_thread = threading.Thread(target=self._ai_loop, daemon=True)
        self.capture_thread.start()
        self.ai_thread.start()
        return True
        
    def stop(self):
        self.running = False
        if self.capture_thread:
            self.capture_thread.join(timeout=2)
            self.capture_thread = None
        if self.ai_thread:
            self.ai_thread.join(timeout=2)
            self.ai_thread = None
        if self.cap:
            self.cap.release()
            self.cap = None
            
        # Publish offline status
        self._publish_vision(0, 0, "offline")
        try:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        except Exception:
            pass
            
    def _publish_vision(self, count, conf, status):
        topic = f"rooms/{ROOM_ID}/vision"
        payload = {
            "cameraId": CAMERA_ID,
            "roomId": ROOM_ID,
            "personCount": count,
            "confidenceAverage": conf,
            "cameraStatus": status,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        try:
            self.mqtt_client.publish(topic, json.dumps(payload))
        except Exception as e:
            logger.error(f"Publish error: {e}")

    def _capture_loop(self):
        """Continuous high-FPS capture loop to keep stream smooth and buffer latency zero."""
        while self.running and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.05)
                continue
                
            frame = cv2.resize(frame, (640, 480))
            self.raw_frame = frame
            
            # Overlay latest bounding boxes on live frame
            display_frame = frame.copy()
            with self.lock:
                boxes = list(self.latest_boxes)
                count = self.person_count
                
            for (x1, y1, x2, y2, conf) in boxes:
                cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(display_frame, f"Person {conf:.2f}", (x1, max(y1 - 10, 0)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            cv2.putText(display_frame, f"Count: {count}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            self.latest_frame = display_frame
            time.sleep(0.03)  # ~30 FPS

    def _ai_loop(self):
        """Asynchronous AI detection loop running periodically without starving CPU."""
        last_publish_time = 0
        while self.running:
            if self.raw_frame is None:
                time.sleep(0.1)
                continue
                
            input_frame = self.raw_frame.copy()
            
            try:
                # Use imgsz=320 to significantly accelerate inference on CPU
                results = self.model(input_frame, classes=[0], conf=YOLO_CONFIDENCE, imgsz=320, verbose=False)
                
                person_count = 0
                conf_sum = 0
                boxes = []
                
                for result in results:
                    for box in result.boxes:
                        person_count += 1
                        conf = float(box.conf[0])
                        conf_sum += conf
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        boxes.append((x1, y1, x2, y2, conf))
                        
                with self.lock:
                    self.latest_boxes = boxes
                    self.person_count = person_count
                    
                avg_conf = conf_sum / person_count if person_count > 0 else 0
                
                current_time = time.time()
                if current_time - last_publish_time > 5:
                    self._publish_vision(person_count, avg_conf, "online")
                    last_publish_time = current_time
            except Exception as e:
                logger.error(f"AI inference error: {e}")
                
            time.sleep(0.8)  # Run AI detection ~1 time/sec: responsive yet low CPU

camera_service = CameraService()
