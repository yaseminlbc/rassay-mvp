from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import SessionLocal
from app.models import ChurnPrediction, XAIFactor
from app import schemas

# Dökümandaki formata uygun router tanımı
router = APIRouter(
    prefix="/api/v1/clients",
    tags=["Churn Analytics"]
)

# Veritabanı bağlantısı için bağımlılık (Dependency)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/{client_id}/risk", response_model=schemas.ChurnRiskResponse)
def get_client_risk(client_id: int, db: Session = Depends(get_db)):
    """Belirli bir müşterinin en güncel churn risk skorunu getirir."""
    
    prediction = db.query(ChurnPrediction).filter(ChurnPrediction.company_id == client_id).first()
    
    if not prediction:
        raise HTTPException(status_code=404, detail="Bu müşteri için henüz bir risk tahmini bulunmuyor.")
        
    return prediction

@router.get("/{client_id}/xai", response_model=List[schemas.XAIFactorResponse])
def get_client_xai(client_id: int, db: Session = Depends(get_db)):
    """Belirli bir müşterinin XAI (SHAP) etki faktörlerini getirir."""
    
    # Önce müşterinin tahmin ID'sini bul
    prediction = db.query(ChurnPrediction).filter(ChurnPrediction.company_id == client_id).first()
    
    if not prediction:
        raise HTTPException(status_code=404, detail="Bu müşteri için tahmin bulunamadı, dolayısıyla XAI verisi de yok.")
        
    # Tahmin ID'sine bağlı XAI faktörlerini getir
    xai_data = db.query(XAIFactor).filter(XAIFactor.prediction_id == prediction.prediction_id).all()
    
    if not xai_data:
        raise HTTPException(status_code=404, detail="Bu müşteri için XAI (SHAP) analizi henüz oluşturulmamış.")
        
    return xai_data
