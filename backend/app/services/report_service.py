import csv
import io
from datetime import datetime
from sqlalchemy.orm import Session
from app import models
from app.services import prediction_service
from app.services.customer_service import _time_ago


def generate_churn_risk_csv(db: Session) -> str:
    # DÜZELTME: models.Company -> models.Customer
    customers = db.query(models.Customer).all()

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        "company_id", "company_name", "plan_type", "risk_score",
        "risk_level", "top_risk_factor", "account_owner", "last_login",
    ])
    writer.writeheader()

    for c in customers:
        # Tahmin verilerini çek
        pred = prediction_service.get_latest_prediction(c.company_id, db)
        
        # Son giriş bilgisini çek
        last_usage = (
            db.query(models.UsageData)
            .filter(models.UsageData.company_id == c.company_id)
            .order_by(models.UsageData.timestamp.desc())
            .first()
        )
        
        # İlişkili abonelik verisi
        sub = getattr(c, 'subscription', None)
        
        # Dinamik isim kontrolü (company_name veya name)
        c_name = getattr(c, 'company_name', getattr(c, 'name', 'Unknown'))

        writer.writerow({
            "company_id":      c.company_id,
            "company_name":    c_name,
            "plan_type":       sub.plan_type if sub else "Standard",
            "risk_score":      pred.risk_score if pred else "",
            "risk_level":      pred.risk_level if pred else "",
            "top_risk_factor": pred.top_risk_factor if pred else "",
            "account_owner":   getattr(c, 'account_owner', 'Unassigned'),
            "last_login":      _time_ago(last_usage.timestamp) if last_usage else "N/A",
        })

    return output.getvalue()

