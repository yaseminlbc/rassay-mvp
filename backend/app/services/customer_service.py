from datetime import datetime
from sqlalchemy.orm import Session
from app import models, schemas
from app.services import prediction_service

def _time_ago(dt: datetime) -> str:
    if not dt:
        return "N/A"
    diff = datetime.now() - dt
    if diff.days >= 1:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    hours = diff.seconds // 3600
    if hours >= 1:
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    return "Just now"

def get_customer_list(
    db: Session,
    risk_level: str | None = None,
    search: str | None = None,
) -> list[schemas.CustomerListItem]:
    """Dashboard ana tablosu için müşteri listesini döner."""
    customers = db.query(models.Customer).limit(100).all()
    result = []

    for c in customers:
        pred = prediction_service.get_latest_prediction(c.company_id, db)

        if risk_level and (pred is None or pred.risk_level != risk_level):
            continue

        name_in_db = getattr(c, 'company_name', getattr(c, 'name', None))
        company_display_name = name_in_db if name_in_db else c.company_id
        
        if search and search.lower() not in company_display_name.lower():
            continue

        result.append(schemas.CustomerListItem(
            id=c.id,
            company_id=c.company_id,
            company_name=company_display_name,
            plan_type=getattr(c, 'plan_type', 'Enterprise'),
            risk_score=pred.risk_score if pred else 0.0,
            risk_level=pred.risk_level if pred else "Low",
            top_risk_factor=pred.top_risk_factor if pred else "None",
            account_owner=getattr(c, 'account_owner', 'Unassigned'),
            churn_status=c.churn_status if hasattr(c, 'churn_status') else 0
        ))

    result.sort(key=lambda x: x.risk_score or 0, reverse=True)
    return result

def get_customer_detail(company_id: str, db: Session) -> schemas.CustomerDetail | None:
    """Müşteri detay sayfası (XAI sayfası) için gerekli tüm verileri toplar."""
    c = db.query(models.Customer).filter(models.Customer.company_id == company_id).first()
    if not c:
        return None

    # KRİTİK DÜZELTME: Detay sayfasına risk skoru ve seviyesini ekliyoruz
    # Bu satır olmazsa frontend "NaN" hatası verir.
    pred = prediction_service.get_latest_prediction(company_id, db)

    name_in_db = getattr(c, 'company_name', getattr(c, 'name', None))
    company_display_name = name_in_db if name_in_db else c.company_id

    # Son 30 günlük kullanım logları
    usage_logs = (
        db.query(models.UsageData)
        .filter(models.UsageData.company_id == company_id)
        .order_by(models.UsageData.timestamp.desc())
        .limit(30)
        .all()
    )
    
    # Detay kartları için metrikler
    logins_30 = sum(u.login_count or 0 for u in usage_logs)
    active_users = usage_logs[0].active_users if usage_logs else 0
    
    # DAU/MAU hesabı (NaN korumalı)
    dau_mau = round((active_users / max(logins_30, 1)) * 100, 1) if logins_30 else 0

    return schemas.CustomerDetail(
        id=c.id,
        company_id=c.company_id,
        company_name=company_display_name,
        plan_type=getattr(c, 'plan_type', None),
        account_owner=getattr(c, 'account_owner', 'Unassigned'),
        risk_score=float(pred.risk_score) if pred else 0.0,
        risk_level=pred.risk_level if pred else "Low",
        top_risk_factor=pred.top_risk_factor if pred else "None",
        account_age_months=getattr(c, 'account_age_months', 0),
        mrr_value=float(getattr(c, 'mrr_value', 0.0)),
        support_tickets=getattr(c, 'support_tickets', 0),
        login_count=logins_30,
        active_users=active_users,
        dau_mau_ratio=dau_mau,
        key_feature_adoption=getattr(c, 'key_feature_adoption', 0),
        renewal_days=getattr(c, 'renewal_days', 0),
        churn_status=c.churn_status if hasattr(c, 'churn_status') else 0,
        created_at=getattr(c, 'created_at', datetime.now())
    )

def get_usage_trend(company_id: str, db: Session) -> schemas.UsageTrendResponse:
    """Detay sayfasındaki çizgi grafik (Engagement History) verisini hazırlar."""
    logs = (
        db.query(models.UsageData)
        .filter(models.UsageData.company_id == company_id)
        .order_by(models.UsageData.timestamp.asc())
        .all()
    )
    
    # Frontend Recharts'ın beklediği formatta (label ve value)
    points = [
        schemas.UsagePoint(
            label=u.timestamp.strftime("%d %b") if u.timestamp else "N/A",
            value=float(u.login_count or 0)
        )
        for u in logs
    ]
    return schemas.UsageTrendResponse(points=points)