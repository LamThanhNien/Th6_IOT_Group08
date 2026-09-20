from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import app.mqtt.handlers as mqtt_handlers

from app.api.auth import router as auth_router
from app.api.rooms import router as rooms_router
from app.api.devices import router as devices_router
from app.api.telemetry import router as telemetry_router
from app.api.commands import router as commands_router
from app.api.alerts import router as alerts_router
from app.api.vision import router as vision_router
from app.api.websocket import router as ws_router
from app.mqtt.client import mqtt_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    mqtt_handlers.main_loop = asyncio.get_running_loop()
    mqtt_client.add_handler(mqtt_handlers.process_mqtt_message)
    mqtt_client.start()
    yield
    mqtt_client.stop()

app = FastAPI(title="Smart Classroom AIoT", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(rooms_router, prefix="/api/rooms", tags=["Rooms"])
app.include_router(devices_router, prefix="/api/devices", tags=["Devices"])
app.include_router(telemetry_router, prefix="/api/telemetry", tags=["Telemetry"])
app.include_router(commands_router, prefix="/api/commands", tags=["Commands"])
app.include_router(alerts_router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(vision_router, prefix="/api/vision", tags=["Vision"])
app.include_router(ws_router, tags=["WebSocket"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Smart Classroom AIoT Backend"}

