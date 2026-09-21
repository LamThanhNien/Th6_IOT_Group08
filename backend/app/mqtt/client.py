import json
import logging
import paho.mqtt.client as mqtt
from app.core.config import settings

logger = logging.getLogger(__name__)

class MQTTClient:
    def __init__(self):
        self.client = mqtt.Client(client_id="fastapi_backend")
        if settings.MQTT_USERNAME:
            self.client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
        
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        
        self.message_handlers = []

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("Connected to MQTT Broker!")
            self.client.subscribe("rooms/+/devices/+/telemetry")
            self.client.subscribe("rooms/+/vision")
            self.client.subscribe("rooms/+/devices/+/status")
            self.client.subscribe("device/+/telemetry")
            self.client.subscribe("device/+/command/ack")
            self.client.subscribe("device/+/status")
        else:
            logger.error(f"Failed to connect to MQTT Broker, return code {rc}")

    def on_disconnect(self, client, userdata, rc):
        logger.warning(f"Disconnected from MQTT Broker with code {rc}")

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            topic = msg.topic
            for handler in self.message_handlers:
                handler(topic, payload)
        except Exception as e:
            logger.error(f"Error parsing MQTT message: {e}")

    def add_handler(self, handler_func):
        self.message_handlers.append(handler_func)

    def publish(self, topic: str, payload: dict):
        try:
            self.client.publish(topic, json.dumps(payload))
            logger.info(f"Published to {topic}")
        except Exception as e:
            logger.error(f"Error publishing to {topic}: {e}")

    def start(self):
        try:
            self.client.connect(settings.MQTT_HOST, settings.MQTT_PORT, 60)
            self.client.loop_start()
        except Exception as e:
            logger.error(f"MQTT connect error: {e}")

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()

mqtt_client = MQTTClient()

