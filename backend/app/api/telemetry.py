from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import get_db
from app.models.telemetry import Telemetry
from app.schemas.telemetry import TelemetryResponse
from app.services.auth import get_current_user

router = APIRouter()

@router.get("/latest", response_model=List[TelemetryResponse])
def get_latest_telemetry(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Group by device_id and get latest - simple approach for SQLite/Postgres
    from sqlalchemy import func
    subquery = db.query(Telemetry.device_id, func.max(Telemetry.timestamp).label("max_ts")).group_by(Telemetry.device_id).subquery()
    results = db.query(Telemetry).join(subquery, (Telemetry.device_id == subquery.c.device_id) & (Telemetry.timestamp == subquery.c.max_ts)).all()
    return results

@router.get("/history", response_model=List[TelemetryResponse])
def get_telemetry_history(device_id: str = None, room_id: str = None, limit: int = 100, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    query = db.query(Telemetry)
    if device_id:
        query = query.filter(Telemetry.device_id == device_id)
    if room_id:
        query = query.filter(Telemetry.room_id == room_id)
    return query.order_by(Telemetry.timestamp.desc()).limit(limit).all()

