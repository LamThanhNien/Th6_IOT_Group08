from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import cv2
import time
from app.camera import camera_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto start camera on boot
    camera_service.start()
    yield
    camera_service.stop()

app = FastAPI(title="AI Camera Service", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def generate_frames():
    encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), 75]
    while True:
        if camera_service.latest_frame is not None:
            ret, buffer = cv2.imencode('.jpg', camera_service.latest_frame, encode_params)
            if ret:
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.04) # ~25 FPS for smooth video stream

@app.get("/api/camera/stream")
def video_stream():
    if not camera_service.running:
        raise HTTPException(status_code=503, detail="Camera is not running")
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.post("/api/camera/start")
async def start_camera():
    success = camera_service.start()
    if not success:
        raise HTTPException(status_code=500, detail="Failed to start camera")
    return {"message": "Camera started"}

@app.post("/api/camera/stop")
async def stop_camera():
    camera_service.stop()
    return {"message": "Camera stopped"}

@app.get("/api/camera/status")
async def get_status():
    return {
        "running": camera_service.running,
        "person_count": camera_service.person_count
    }

