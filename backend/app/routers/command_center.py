from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import command_center_service

router = APIRouter(prefix="/command-center", tags=["Command Center"])


@router.get("/health-score")
def health_score(db: Session = Depends(get_db)):
    return command_center_service.get_health_score(db)


@router.get("/notifications")
def notifications(db: Session = Depends(get_db)):
    return command_center_service.get_notifications(db)
