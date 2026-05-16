from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app import models

def get_summary(db: Session):
    """
    Dashboard'un en üstündeki KPI kartlarını doldurur.
    """
    # 1. Toplam Müşteri Sayısı (Customer tablosundan)
    total_clients = db.query(models.Customer).count()

    # 2. Risk Grupları (ChurnPrediction tablosundaki en güncel kayıtlardan)
    high_risk = db.query(models.ChurnPrediction).filter(models.ChurnPrediction.risk_level == "High").count()
    medium_risk = db.query(models.ChurnPrediction).filter(models.ChurnPrediction.risk_level == "Medium").count()
    low_risk = db.query(models.ChurnPrediction).filter(models.ChurnPrediction.risk_level == "Low").count()

    # 3. Risk Altındaki Toplam Gelir (Yüksek riskli müşterilerin toplam MRR'ı)
    # Customer ve ChurnPrediction tablolarını company_id üzerinden birleştiriyoruz
    revenue_at_risk = db.query(func.sum(models.Customer.mrr_value)).join(
        models.ChurnPrediction, models.Customer.company_id == models.ChurnPrediction.company_id
    ).filter(models.ChurnPrediction.risk_level == "High").scalar() or 0

    # 4. Portföy Sağlık Puanı (Basit bir ağırlıklı ortalama)
    health_score = 100
    if total_clients > 0:
        # Yüksek riskliler 0, Orta riskliler 50, Düşük riskliler 100 puan üzerinden
        health_score = ((low_risk * 100) + (medium_risk * 50) + (high_risk * 0)) / total_clients

    return {
        "total_clients": total_clients,
        "high_risk_count": high_risk,
        "medium_risk_count": medium_risk,
        "low_risk_count": low_risk,
        "revenue_at_risk": float(revenue_at_risk),
        "average_health_score": round(health_score, 1),
        "last_sync": datetime.now().strftime("%H:%M")
    }

def get_risk_trend(range_str: str, db: Session):
    """
    Zaman içindeki risk değişim grafiğini (LineChart) doldurur.
    """
    trends = []
    # Son 7 günü kapsayan bir döngü kuruyoruz
    for i in range(6, -1, -1):
        target_date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        
        # Gerçek bir sistemde her güne ait tahmin verisi çekilir. 
        # Şu an veritabanında tek bir 'run' olduğu için mevcut rakamları tarihe yayıyoruz.
        high_count = db.query(models.ChurnPrediction).filter(models.ChurnPrediction.risk_level == "High").count()
        medium_count = db.query(models.ChurnPrediction).filter(models.ChurnPrediction.risk_level == "Medium").count()
        low_count = db.query(models.ChurnPrediction).filter(models.ChurnPrediction.risk_level == "Low").count()

        trends.append({
            "period": target_date, # Frontend 'period' anahtarını bekliyor
            "high": high_count,
            "medium": medium_count,
            "low": low_count
        })
    
    return trends

def get_risk_distribution(db: Session):
    """
    Pasta grafik (PieChart) için risk dağılımını döner.
    """
    high = db.query(models.ChurnPrediction).filter(models.ChurnPrediction.risk_level == "High").count()
    medium = db.query(models.ChurnPrediction).filter(models.ChurnPrediction.risk_level == "Medium").count()
    low = db.query(models.ChurnPrediction).filter(models.ChurnPrediction.risk_level == "Low").count()

    return [
        {"name": "High Risk", "value": high},
        {"name": "Medium Risk", "value": medium},
        {"name": "Low Risk", "value": low}
    ]