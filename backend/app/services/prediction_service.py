from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app import models


def classify_risk_level(score: float) -> str:
    """Skora göre risk kategorisini belirle."""
    if score > 75:
        return "High"
    if score >= 40:
        return "Medium"
    return "Low"


def calculate_risk_score(features: dict) -> float:
    """
    Kural tabanlı scoring mantığı. 
    Frontend tarafındaki gauge (gösterge) 0-100 arası çalıştığı için sonucu 100 üzerinden döndürür.
    """
    login_drop       = features.get("login_drop_pct", 0)
    active_user_drop = features.get("active_user_drop_pct", 0)
    ticket_count     = features.get("support_ticket_count", 0)
    renewal_days     = features.get("renewal_days", 90)
    feature_drop     = features.get("feature_usage_drop_pct", 0)

    # Ağırlıklı risk puanı hesaplama
    score = (
        15
        + login_drop       * 0.40
        + active_user_drop * 0.25
        + min(ticket_count, 10) * 1.5
        + feature_drop     * 0.20
    )
    if renewal_days <= 30:
        score += 10

    return max(0.0, min(100.0, round(score, 2)))


def _compute_features(usage_logs: list, subscription) -> dict:
    """UsageData listesinden ML feature'larını türet."""
    if not usage_logs:
        return {}

    now = datetime.now()
    # Son 14 gün vs önceki 45 gün karşılaştırması
    recent = [u for u in usage_logs if (now - u.timestamp).days <= 14]
    older  = [u for u in usage_logs if 14 < (now - u.timestamp).days <= 60]

    def avg(lst, attr):
        vals = [getattr(x, attr) or 0 for x in lst]
        return sum(vals) / len(vals) if vals else 0

    recent_logins  = avg(recent, "login_count")
    older_logins   = avg(older,  "login_count") or 1
    recent_active  = avg(recent, "active_users")
    older_active   = avg(older,  "active_users") or 1
    recent_feat    = avg(recent, "feature_usage_count")
    older_feat     = avg(older,  "feature_usage_count") or 1
    ticket_count   = sum(getattr(u, "support_ticket_count") or 0 for u in recent)

    # Düşüş yüzdelerini hesapla
    login_drop       = max(0, (older_logins - recent_logins) / older_logins * 100)
    active_user_drop = max(0, (older_active - recent_active) / older_active * 100)
    feature_drop     = max(0, (older_feat - recent_feat) / older_feat * 100)

    # Yenileme gün sayısı
    renewal_days = 90
    if subscription and hasattr(subscription, 'renewal_date') and subscription.renewal_date:
        rd = subscription.renewal_date
        rd_dt = datetime(rd.year, rd.month, rd.day)
        renewal_days = max(0, (rd_dt - now).days)

    return {
        "login_drop_pct":         round(login_drop, 2),
        "active_user_drop_pct":   round(active_user_drop, 2),
        "feature_usage_drop_pct": round(feature_drop, 2),
        "support_ticket_count":   ticket_count,
        "renewal_days":           renewal_days,
    }


def _top_risk_factor(features: dict) -> str:
    """En büyük risk faktörünü belirle (Frontend'de tablo sütununda görünür)."""
    mapping = {
        "login_drop_pct":         "Decreased Login Frequency",
        "active_user_drop_pct":   "Active User Drop",
        "feature_usage_drop_pct": "Low Core Feature Usage",
        "support_ticket_count":   "High Support Ticket Volume",
    }
    top = max(
        {k: v for k, v in features.items() if k != "renewal_days"},
        key=lambda k: features.get(k, 0),
        default="login_drop_pct",
    )
    return mapping.get(top, "Usage Drop")


def run_prediction_for_customer(customer, db: Session) -> models.ChurnPrediction:
    """
    Compute churn risk for a single customer and persist ChurnPrediction +
    XAIFactor rows.

    Primary path: XGBoost + SHAP via xgboost_service (requires trained model).
    Fallback path: rule-based scoring when the model file is not yet available.
    """
    from app.services import xgboost_service

    if xgboost_service.is_model_available():
        feature_values = {
            'mrr_value':          float(customer.mrr_value or 0),
            'account_age_months': int(customer.account_age_months or 0),
            'support_tickets':    int(customer.support_tickets or 0),
            'login_count':        int(customer.login_count or 0),
            'plan_type':          str(customer.plan_type or ''),
        }
        result       = xgboost_service.predict_single(feature_values)
        risk_score   = result['risk_score']          # already 0-1
        risk_level   = result['risk_level']
        top_factor   = result['top_risk_factor']
        shap_factors = result['shap_factors']
        model_ver    = "v2.0-xgboost-shap"
    else:
        # Rule-based fallback until the model is trained for the first time
        usage_logs = (
            db.query(models.UsageData)
            .filter(models.UsageData.company_id == customer.company_id)
            .order_by(models.UsageData.timestamp.asc())
            .all()
        )
        features   = _compute_features(usage_logs, getattr(customer, 'subscription', None))
        raw_score  = calculate_risk_score(features)
        risk_score = round(raw_score / 100.0, 4)
        risk_level = classify_risk_level(raw_score)
        top_factor = _top_risk_factor(features) if features else "Insufficient data"
        shap_factors = []
        model_ver    = "v1.1-hybrid"

    pred = models.ChurnPrediction(
        company_id=str(customer.company_id),
        calculation_date=datetime.now(),
        risk_score=risk_score,
        risk_level=risk_level,
        top_risk_factor=top_factor,
        model_version=model_ver,
    )
    db.add(pred)
    db.flush()  # obtain prediction_id before inserting child XAI rows

    for factor in shap_factors[:3]:
        db.add(models.XAIFactor(
            prediction_id=pred.prediction_id,
            feature_name=factor['feature_name'],
            impact_value=factor['impact_value'],
            impact_level=factor['impact_level'],
            direction=factor['direction'],
        ))

    return pred


def get_latest_prediction(company_id: str, db: Session):
    """Müşterinin en güncel tahmin sonucunu getir."""
    return (
        db.query(models.ChurnPrediction)
        .filter(models.ChurnPrediction.company_id == company_id)
        .order_by(models.ChurnPrediction.calculation_date.desc())
        .first()
    )


def get_usage_history_days(company_id: str, db: Session) -> int:
    """Kaç günlük kullanım geçmişi olduğunu hesapla."""
    oldest = (
        db.query(models.UsageData)
        .filter(models.UsageData.company_id == company_id)
        .order_by(models.UsageData.timestamp.asc())
        .first()
    )
    if not oldest:
        return 0
    return (datetime.now() - oldest.timestamp).days

