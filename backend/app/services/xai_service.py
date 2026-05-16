
from datetime import datetime
from sqlalchemy.orm import Session
from app.services import prediction_service
from app import models
from app.schemas import XAIResponse, XAIFactor


_FACTOR_TEMPLATES = [
    {
        "feature": "Decreased Login Frequency",
        "field":   "login_drop_pct",
        "weight":  0.35,
    },
    {
        "feature": "Low Core Feature Usage",
        "field":   "feature_usage_drop_pct",
        "weight":  0.20,
    },
    {
        "feature": "Active User Drop",
        "field":   "active_user_drop_pct",
        "weight":  0.30,
    },
    {
        "feature": "Support Ticket Volume Increase",
        "field":   "support_ticket_count",
        "weight":  0.15,
    },
]


def _impact_level(impact: float) -> str:
    if impact >= 0.35:
        return "High"
    if impact >= 0.20:
        return "Medium"
    return "Low"


def _mock_top_factors(company_id: int, db: Session) -> list[XAIFactor]:
    """
    Kayıtlı faktörleri getir veya hesapla.
    """
    pred = prediction_service.get_latest_prediction(company_id, db)
    
    # Eğer veritabanında hazır faktörler varsa onları dön
    if pred and hasattr(pred, 'xai_factors') and pred.xai_factors:
        return [
            XAIFactor(
                feature_name=f.feature_name,
                impact_value=round(f.impact_value, 2),
                impact_level=f.impact_level,
                direction="Positive" # Churn riskini artırdığı için pozitif etki
            )
            for f in sorted(pred.xai_factors, key=lambda x: x.impact_value, reverse=True)[:3]
        ]

    # Fallback: UsageData üzerinden canlı hesapla
    usage_logs = (
        db.query(models.UsageData)
        .filter(models.UsageData.company_id == company_id)
        .order_by(models.UsageData.timestamp.desc())
        .limit(60)
        .all()
    )
    
    if not usage_logs:
        return []

    now = datetime.now()
    recent = [u for u in usage_logs if (now - u.timestamp).days <= 7]
    older  = [u for u in usage_logs if 7 < (now - u.timestamp).days <= 30]

    def avg(lst, attr):
        vals = [getattr(x, attr) or 0 for x in lst]
        return sum(vals) / len(vals) if vals else 0

    raw_features = {
        "login_drop_pct":         max(0, (avg(older, "login_count") - avg(recent, "login_count")) / max(avg(older, "login_count"), 1) * 100),
        "feature_usage_drop_pct": max(0, (avg(older, "feature_usage_count") - avg(recent, "feature_usage_count")) / max(avg(older, "feature_usage_count"), 1) * 100),
        "active_user_drop_pct":   max(0, (avg(older, "active_users") - avg(recent, "active_users")) / max(avg(older, "active_users"), 1) * 100),
        "support_ticket_count":   sum(getattr(u, "support_ticket_count") or 0 for u in recent),
    }

    factors = []
    total = sum(raw_features.values()) or 1
    for tmpl in _FACTOR_TEMPLATES:
        raw = raw_features.get(tmpl["field"], 0)
        impact = round((raw / total) * tmpl["weight"] * 2, 2) if total else tmpl["weight"]
        factors.append(XAIFactor(
            feature_name=tmpl["feature"],
            impact_value=min(impact, 0.99),
            impact_level=_impact_level(impact),
            direction="Positive"
        ))

    return sorted(factors, key=lambda f: f.impact_value, reverse=True)[:3]


def get_xai_explanation(company_id: int, db: Session) -> XAIResponse:
    # DÜZELTME: models.Company -> models.Customer
    customer = db.query(models.Customer).filter(models.Customer.company_id == company_id).first()
    
    if not customer:
        return XAIResponse(
            prediction_id=0,
            factors=[],
            # Frontend'e hata mesajı için opsiyonel alanlar eklenebilir
        )

    pred = prediction_service.get_latest_prediction(company_id, db)
    risk_score = pred.risk_score if pred else 0.0

    # Faktörleri al
    factors = _mock_top_factors(company_id, db)
    
    return XAIResponse(
        prediction_id=pred.prediction_id if pred else 0,
        factors=factors
    )
