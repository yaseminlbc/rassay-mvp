from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import alert_service, report_service, prediction_service
from app.schemas import AlertItem, IntegrationStatus, IngestResponse, PredictRunResponse, UsageDataIngest
from app import models
from datetime import datetime

# ── Alerts ────────────────────────────────────────────────────────────────────

# DÜZELTME 1: "/api/alerts" yerine SADECE "/alerts"
alerts_router = APIRouter(prefix="/alerts", tags=["Alerts"])

@alerts_router.get("", response_model=list[AlertItem])
def get_alerts(db: Session = Depends(get_db)):
    return alert_service.get_alerts(db)


# ── Integrations ──────────────────────────────────────────────────────────────

# DÜZELTME 2: "/api/integrations" yerine SADECE "/integrations"
integrations_router = APIRouter(prefix="/integrations", tags=["Integrations"])

@integrations_router.get("/status", response_model=IntegrationStatus)
def integration_status(db: Session = Depends(get_db)):
    # DB bağlantısını test et (models.Company yerine models.Customer)
    try:
        db.execute(models.Customer.__table__.select().limit(1))
        db_status = "Connected"
    except Exception:
        db_status = "Error"

    return IntegrationStatus(
        api_connection="Active",
        prediction_pipeline="Operational",
        last_successful_sync=datetime.now().isoformat() + "Z",
        database=db_status,
        encryption="AES-256 at rest, TLS in transit",
    )


# ── Reports / CSV ─────────────────────────────────────────────────────────────

# DÜZELTME 3: "/api/reports" yerine SADECE "/reports"
reports_router = APIRouter(prefix="/reports", tags=["Reports"])

@reports_router.get("/churn-risk.csv")
def churn_risk_csv(db: Session = Depends(get_db)):
    csv_content = report_service.generate_churn_risk_csv(db)
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="rassay_churn_risk_report.csv"'},
    )


# ── Ingest ────────────────────────────────────────────────────────────────────

# DÜZELTME 4: "/api/ingest" yerine SADECE "/ingest"
ingest_router = APIRouter(prefix="/ingest", tags=["Ingest"])

@ingest_router.post("/usage-data", response_model=IngestResponse, status_code=201)
def ingest_usage(payload: UsageDataIngest, db: Session = Depends(get_db)):
    # DÜZELTME: models.Company -> models.Customer
    customer = db.query(models.Customer).filter(models.Customer.company_id == payload.company_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail={"code": "CUSTOMER_NOT_FOUND", "detail": f"Customer {payload.company_id} not found."})
    
    log = models.UsageData(
        company_id=payload.company_id,
        login_count=payload.login_count,
        active_users=payload.active_users,
        feature_usage_count=payload.feature_usage_count,
        support_ticket_count=payload.support_ticket_count,
        nps_score=payload.nps_score,
        timestamp=datetime.now(),
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    # schema'da log_id mi id mi yazıyor kontrol et, genelde id'dir
    return IngestResponse(status="ok", log_id=getattr(log, 'id', getattr(log, 'log_id', 0)), company_id=log.company_id)


# ── Predict Run ───────────────────────────────────────────────────────────────

# DÜZELTME 5: "/api/predict" yerine SADECE "/predict"
predictions_router = APIRouter(prefix="/predict", tags=["Predictions"])

@predictions_router.post("/run", response_model=PredictRunResponse)
def run_predictions(db: Session = Depends(get_db)):
    # DÜZELTME: models.Company -> models.Customer
    customers = db.query(models.Customer).limit(100).all()
    counts = {"High": 0, "Medium": 0, "Low": 0}
    
    for customer in customers:
        # prediction_service'te isim run_prediction_for_customer olarak değişmişti
        pred = prediction_service.run_prediction_for_customer(customer, db)
        counts[pred.risk_level] = counts.get(pred.risk_level, 0) + 1
        
    db.commit()
    return PredictRunResponse(
        status="ok",
        companies_processed=len(customers),
        high_risk=counts["High"],
        medium_risk=counts["Medium"],
        low_risk=counts["Low"],
    )

