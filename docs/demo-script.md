# K?ch b?n Demo Smart Classroom AIoT

1. **Kh?i d?ng h? t?ng**: Ð?m b?o Docker ch?y `docker-compose up -d`.
2. **Kh?i d?ng Backend**: Ch?y `python -m uvicorn app.main:app` trong `backend`.
3. **Kh?i d?ng Simulator**: Ch?y `python src/main.py` trong `device-simulator`.
4. **Kh?i d?ng AI Camera**: Ch?y `python -m uvicorn app.main:app` trong `ai-camera-service`.
5. **M? Web Dashboard**: M? trình duy?t t?i `http://localhost:5173`.
6. **Ðang nh?p**: Dùng tài kho?n `admin@smartclass.local` / `Admin@123`.
7. **Ki?m tra AI Camera**: Di chuy?n tru?c camera d? YOLO d?m s? ngu?i và c?p nh?t Dashboard.
8. **Ki?m tra Telemetry**: Xem nhi?t d? và d? ?m do Simulator d?y lên.
9. **Ki?m tra C?nh báo**: B?t ch? d? High Temp ? Simulator d? kích ho?t c?nh báo nhi?t d? cao.
10. **Ði?u khi?n thi?t b?**: B?t/t?t Qu?t, Ðèn t? giao di?n và theo dõi log c?a Simulator d? xác nh?n l?nh MQTT.

