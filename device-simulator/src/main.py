import os
import time
import json
import random
import logging
from datetime import datetime
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")
ROOM_ID = os.getenv("ROOM_ID", "ROOM_01")
DEVICE_ID = os.getenv("DEVICE_ID", "ESP32_ROOM_01")
INTERVAL = int(os.getenv("TELEMETRY_INTERVAL_SECONDS", 5))

# Device state
state = {
    "fan": False,
    "led": False,
    "high_temp_mode": False
}

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to MQTT Broker!")
        topic = f"rooms/{ROOM_ID}/devices/{DEVICE_ID}/commands"
        client.subscribe(topic)
        logging.info(f"Subscribed to {topic}")
    else:
        logging.error(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        logging.info(f"Received command: {payload}")
        
        command_id = payload.get("commandId")
        action = payload.get("action")
        value = payload.get("value")
        
        if action == "SET_FAN":
            state["fan"] = bool(value)
            status_msg = "Fan turned " + ("ON" if state["fan"] else "OFF")
        elif action == "SET_LED":
            state["led"] = bool(value)
            status_msg = "LED turned " + ("ON" if state["led"] else "OFF")
        elif action == "ENABLE_HIGH_TEMP":
            state["high_temp_mode"] = bool(value)
            status_msg = "High temp mode " + ("ENABLED" if state["high_temp_mode"] else "DISABLED")
        else:
            status_msg = f"Unknown action {action}"

        # Send status back
        status_topic = f"rooms/{ROOM_ID}/devices/{DEVICE_ID}/status"
        status_payload = {
            "commandId": command_id,
            "deviceId": DEVICE_ID,
            "fan": state["fan"],
            "led": state["led"],
            "status": "success",
            "message": status_msg,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        client.publish(status_topic, json.dumps(status_payload))
        logging.info(f"Sent status: {status_payload}")
        
    except Exception as e:
        logging.error(f"Error parsing message: {e}")

def main():
    client = mqtt.Client(client_id=DEVICE_ID)
    if MQTT_USERNAME:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        
    client.on_connect = on_connect
    client.on_message = on_message

    logging.info(f"Connecting to MQTT broker at {MQTT_HOST}:{MQTT_PORT}...")
    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.loop_start()

    telemetry_topic = f"rooms/{ROOM_ID}/devices/{DEVICE_ID}/telemetry"

    try:
        while True:
            # Generate dummy data
            if state["high_temp_mode"]:
                temp = round(random.uniform(32.0, 36.0), 1)
            else:
                temp = round(random.uniform(25.0, 29.0), 1)
            
            humidity = random.randint(50, 70)

            telemetry = {
                "deviceId": DEVICE_ID,
                "roomId": ROOM_ID,
                "temperature": temp,
                "humidity": humidity,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }

            client.publish(telemetry_topic, json.dumps(telemetry))
            logging.info(f"Published telemetry: Temp: {temp}C, Hum: {humidity}%")
            
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        logging.info("Stopping simulator...")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()

