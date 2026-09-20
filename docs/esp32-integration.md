# Hu?ng d?n tích h?p ESP32 th?t

Sau khi test Simulator thành công, b?n có th? n?p code cho ESP32 th?t:

## So d? chân
- DHT22: GPIO 15
- LED: GPIO 2
- Fan (Relay): GPIO 4

## C?u hình
- S?a `WIFI_SSID` và `WIFI_PASSWORD` trong code Arduino/ESP-IDF.
- S?a `MQTT_HOST` tr? v? IP c?a máy tính dang ch?y Broker.

## MQTT Topics
- Telemetry: `rooms/ROOM_01/devices/ESP32_ROOM_01/telemetry`
- Command Sub: `rooms/ROOM_01/devices/ESP32_ROOM_01/commands`
- Status Pub: `rooms/ROOM_01/devices/ESP32_ROOM_01/status`

