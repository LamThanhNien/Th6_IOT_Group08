# ESP32 Firmware - Smart Classroom (Chương 6)

Dự án firmware ESP-IDF chuẩn hóa tương tự cấu trúc của **BT5**, được cập nhật đầy đủ sơ đồ chân, các MQTT Topic và cấu trúc bản tin tương thích hệ thống quản trị Chương 6.

---

## 1. Sơ đồ đấu nối phần cứng (Hardware Pinout)

Theo tài liệu [esp32-integration.md](../docs/esp32-integration.md):

| Thiết bị | Chân ESP32 | Ghi chú |
|---|---|---|
| **DHT22 (Data)** | **GPIO 15** | Cần trở kéo lên (pull-up 4.7k - 10k lên 3.3V nếu dùng module rời không có sẵn trở) |
| **Đèn LED** | **GPIO 2** | LED Onboard hoặc LED gắn ngoài qua trở 220Ω |
| **Quạt (Relay / Fan)** | **GPIO 4** | Chân tín hiệu điều khiển Relay đóng/ngắt quạt |
| **VCC** | **3.3V / 5V** | Cấp nguồn cho module |
| **GND** | **GND** | Nối chung GND |

---

## 2. Cấu hình MQTT & Topics

- **Broker URI:** `mqtt://192.168.1.183:1883` *(Sửa lại trong `main.c` nếu IP máy chủ đổi)*
- **Client ID:** `ESP32_ROOM_01`
- **Room ID:** `ROOM_01`

### Danh sách Topic:

1. **Telemetry (ESP32 gửi dữ liệu cảm biến định kỳ 5s):**
   - **Topic:** `rooms/ROOM_01/devices/ESP32_ROOM_01/telemetry`
   - **Payload mẫu:**
     ```json
     {
       "deviceId": "ESP32_ROOM_01",
       "roomId": "ROOM_01",
       "temperature": 27.5,
       "humidity": 65.0,
       "timestamp": "2026-09-20T16:00:00Z"
     }
     ```

2. **Commands (ESP32 lắng nghe lệnh điều khiển từ Backend / Dashboard):**
   - **Topic:** `rooms/ROOM_01/devices/ESP32_ROOM_01/commands`
   - **Lệnh hỗ trợ:**
     - `SET_LED`: Bật/Tắt LED (`value`: `true`/`false`)
     - `SET_FAN`: Bật/Tắt Quạt/Relay (`value`: `true`/`false`)
     - `ENABLE_HIGH_TEMP`: Giả lập nhiệt độ cao > 32°C (35.5°C) để test hệ thống cảnh báo tự động

3. **Status (ESP32 phản hồi trạng thái sau khi nhận lệnh hoặc khi Online/Offline):**
   - **Topic:** `rooms/ROOM_01/devices/ESP32_ROOM_01/status`
   - **Payload mẫu:**
     ```json
     {
       "commandId": "cmd-xxx",
       "deviceId": "ESP32_ROOM_01",
       "fan": true,
       "led": false,
       "status": "success",
       "message": "Fan turned ON",
       "timestamp": "2026-09-20T16:00:01Z"
     }
     ```

---

## 3. Cấu hình Wi-Fi

Có 2 cách cấu hình Wi-Fi tiện lợi giống hệt BT5:

### Cách 1: Sửa trong `sdkconfig.defaults`
Mở tệp `sdkconfig.defaults` và sửa SSID cùng mật khẩu Wi-Fi của bạn:
```ini
CONFIG_EXAMPLE_WIFI_SSID="Ten_Wifi_Cua_Ban"
CONFIG_EXAMPLE_WIFI_PASSWORD="Mat_Khau_Wifi"
```

### Cách 2: Cấu hình qua giao diện Menuconfig
Trong terminal ESP-IDF:
```powershell
idf.py menuconfig
```
Di chuyển tới: **Example Connection Configuration** -> Nhập **WiFi SSID** và **WiFi Password** -> Nhấn `S` để lưu và `Q` để thoát.

---

## 4. Hướng dẫn Biên dịch & Nạp Code (Build & Flash)

> **Lưu ý quan trọng trước khi test ESP32 thật:**
> Nếu bạn từng chạy `device-simulator` (bộ giả lập), hãy chắc chắn đã tắt nó đi trước để tránh 2 thiết bị tranh chấp cùng một Client ID `ESP32_ROOM_01` trên Broker Mosquitto.

Mở PowerShell trên máy tính và chạy các lệnh sau:

### Bước 1: Kích hoạt môi trường ESP-IDF (nếu mở terminal mới)
```powershell
$env:IDF_TOOLS_PATH = "C:\Espressif"
$env:IDF_PYTHON_ENV_PATH = "C:\Espressif\tools\python\v5.5.5\venv"
. C:\esp\v5.5.5\esp-idf\export.ps1
cd "d:\Code\IOT\BaiTap\BT6\demo_chuong_6_lt\esp32-firmware"
```

### Bước 2: Chọn chip mục tiêu (nếu chip của bạn là ESP32 hoặc ESP32-S3)
- Đối với chip **ESP32 thường**:
  ```powershell
  idf.py set-target esp32
  ```
- Đối với chip **ESP32-S3**:
  ```powershell
  idf.py set-target esp32s3
  ```

### Bước 3: Biên dịch dự án
```powershell
idf.py build
```

### Bước 4: Nạp vào bo mạch & mở Serial Monitor
*(Thay `COM3` bằng cổng COM thực tế của bo mạch ESP32 trên máy bạn)*
```powershell
idf.py -p COM3 flash monitor
```
*(Để thoát monitor nhấn tổ hợp phím `Ctrl + ]`)*
