from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import get_db
from app.models.vision_detection import VisionDetection
from app.schemas.vision import VisionDetectionResponse
from app.services.auth import get_current_user

router = APIRouter()

@router.get("/latest", response_model=List[VisionDetectionResponse])
def get_latest_vision(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    from sqlalchemy import func
    subquery = db.query(VisionDetection.camera_id, func.max(VisionDetection.timestamp).label("max_ts")).group_by(VisionDetection.camera_id).subquery()
    results = db.query(VisionDetection).join(subquery, (VisionDetection.camera_id == subquery.c.camera_id) & (VisionDetection.timestamp == subquery.c.max_ts)).all()
    return results

@router.get("/history", response_model=List[VisionDetectionResponse])
def get_vision_history(camera_id: str = None, room_id: str = None, limit: int = 100, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    query = db.query(VisionDetection)
    if camera_id:
        query = query.filter(VisionDetection.camera_id == camera_id)
    if room_id:
        query = query.filter(VisionDetection.room_id == room_id)
    return query.order_by(VisionDetection.timestamp.desc()).limit(limit).all()

