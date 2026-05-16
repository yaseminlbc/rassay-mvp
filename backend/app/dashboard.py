from typing import List # Bu mutlaka olmalı
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import dashboard_service
from app.schemas import DashboardSummary, RiskTrendPoint

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary", response_model=DashboardSummary)
def summary(db: Session = Depends(get_db)):
    return dashboard_service.get_summary(db)

@router.get("/trend", response_model=List[RiskTrendPoint]) # Burası List[...] oldu
def trend(
    range: str = Query(default="30d"),
    db: Session = Depends(get_db),
):
    return dashboard_service.get_risk_trend(range, db)

@router.get("/distribution")
def distribution(db: Session = Depends(get_db)):
    return dashboard_service.get_risk_distribution(db)