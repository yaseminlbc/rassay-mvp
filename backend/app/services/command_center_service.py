from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models


def get_health_score(db: Session) -> dict:
    total = db.query(models.Customer).count()
    if total == 0:
        return {
            "overall_score": 0,
            "status": "No Data",
            "components": [],
            "last_updated": datetime.utcnow().isoformat() + "Z",
        }

    high = db.query(models.ChurnPrediction).filter(models.ChurnPrediction.risk_level == "High").count()
    medium = db.query(models.ChurnPrediction).filter(models.ChurnPrediction.risk_level == "Medium").count()
    low = db.query(models.ChurnPrediction).filter(models.ChurnPrediction.risk_level == "Low").count()

    # Customer retention score (High=0, Medium=50, Low=100)
    retention_score = ((low * 100) + (medium * 50)) / total

    # Revenue health: percentage of MRR NOT at high risk
    total_revenue = db.query(func.sum(models.Customer.mrr_value)).scalar() or 0
    revenue_at_risk = (
        db.query(func.sum(models.Customer.mrr_value))
        .join(models.ChurnPrediction, models.Customer.company_id == models.ChurnPrediction.company_id)
        .filter(models.ChurnPrediction.risk_level == "High")
        .scalar()
        or 0
    )
    revenue_score = ((total_revenue - revenue_at_risk) / total_revenue * 100) if total_revenue > 0 else 100

    # Engagement index: penalises high risk more heavily than medium
    engagement_score = max(0.0, 100 - (high / total * 100) - (medium / total * 30))

    overall = retention_score * 0.40 + revenue_score * 0.35 + engagement_score * 0.25

    if overall >= 80:
        status = "Healthy"
    elif overall >= 60:
        status = "Fair"
    elif overall >= 40:
        status = "At Risk"
    else:
        status = "Critical"

    return {
        "overall_score": round(overall, 1),
        "status": status,
        "components": [
            {"name": "Customer Retention", "score": round(retention_score, 1), "weight": 0.40},
            {"name": "Revenue Health", "score": round(revenue_score, 1), "weight": 0.35},
            {"name": "Engagement Index", "score": round(engagement_score, 1), "weight": 0.25},
        ],
        "last_updated": datetime.utcnow().isoformat() + "Z",
    }


def get_notifications(db: Session) -> dict:
    total = db.query(models.Customer).count()
    high = db.query(models.ChurnPrediction).filter(models.ChurnPrediction.risk_level == "High").count()
    medium = db.query(models.ChurnPrediction).filter(models.ChurnPrediction.risk_level == "Medium").count()

    notifications = []
    nid = 1
    now = datetime.utcnow().isoformat() + "Z"

    if high > 0:
        pct = round(high / total * 100, 1) if total else 0
        notifications.append({
            "id": nid,
            "type": "critical",
            "title": "High Churn Risk Alert",
            "message": f"{high} customers ({pct}%) are at high churn risk and need immediate attention.",
            "category": "risk",
            "created_at": now,
        })
        nid += 1

    revenue_at_risk = (
        db.query(func.sum(models.Customer.mrr_value))
        .join(models.ChurnPrediction, models.Customer.company_id == models.ChurnPrediction.company_id)
        .filter(models.ChurnPrediction.risk_level == "High")
        .scalar()
        or 0
    )
    if revenue_at_risk > 10_000:
        notifications.append({
            "id": nid,
            "type": "critical",
            "title": "Revenue at Risk",
            "message": f"${revenue_at_risk:,.0f} MRR is at risk. Prioritise outreach to high-risk accounts.",
            "category": "revenue",
            "created_at": now,
        })
        nid += 1

    if medium > 0:
        pct = round(medium / total * 100, 1) if total else 0
        notifications.append({
            "id": nid,
            "type": "warning",
            "title": "Medium Risk Customers",
            "message": f"{medium} customers ({pct}%) require proactive engagement before they escalate.",
            "category": "risk",
            "created_at": now,
        })
        nid += 1

    notifications.append({
        "id": nid,
        "type": "info",
        "title": "Prediction Pipeline Active",
        "message": f"XGBoost model v2.0 is operational. {total} customers scored successfully.",
        "category": "system",
        "created_at": now,
    })

    unread = sum(1 for n in notifications if n["type"] in ("critical", "warning"))
    return {"unread_count": unread, "notifications": notifications}
