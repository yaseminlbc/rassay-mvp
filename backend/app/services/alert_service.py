from sqlalchemy.orm import Session
from app import models, schemas

def get_alerts(db: Session) -> list[schemas.AlertItem]:
    # Alert tablosundan tüm uyarıları çekiyoruz
    alerts = (
        db.query(models.Alert)
        .order_by(models.Alert.created_at.desc())
        .all()
    )
    
    result = []
    for a in alerts:
        # DÜZELTME: models.Company yerine models.Customer kullanıyoruz
        customer = db.query(models.Customer).filter(models.Customer.company_id == a.company_id).first()
        
        # En son yapılan tahmini çekiyoruz
        pred = (
            db.query(models.ChurnPrediction)
            .filter(models.ChurnPrediction.company_id == a.company_id)
            .order_by(models.ChurnPrediction.calculation_date.desc())
            .first()
        )
        
        # schemas.py içindeki AlertItem ile tam uyumlu eşleştirme
        # Customer tablosundaki alan adın 'name' ise c.name, 'company_name' ise c.company_name yapmalısın
        c_name = "Unknown"
        if customer:
            c_name = getattr(customer, 'company_name', getattr(customer, 'name', 'Unknown'))

        result.append(schemas.AlertItem(
            alert_id=a.alert_id,
            company_id=a.company_id,
            company_name=c_name,
            risk_score=pred.risk_score if pred else None,
            severity=a.severity,
            message=a.message,
            recommended_action=a.recommended_action,
            created_at=a.created_at,
        ))
        
    return result