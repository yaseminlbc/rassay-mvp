from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import customer_service
from app.schemas import CustomerListItem, CustomerDetail, UsageTrendResponse, XAIResponse
from app import models

router = APIRouter(prefix="/customers", tags=["Customers"])

VALID_RISK_LEVELS = {"High", "Medium", "Low"}

# 1. MÜŞTERİ LİSTESİ (DASHBOARD TABLOSU)
@router.get("", response_model=list[CustomerListItem])
def list_customers(
    risk_level: str | None = Query(default=None),
    search:     str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    if risk_level and risk_level != "all" and risk_level not in VALID_RISK_LEVELS:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_RISK_LEVEL", "detail": "risk_level must be one of: High, Medium, Low."},
        )
    return customer_service.get_customer_list(db, risk_level=risk_level, search=search)

# 2. MÜŞTERİ GENEL DETAYI
# DÜZELTME: company_id artık 'str' (String)
@router.get("/{company_id}", response_model=CustomerDetail)
def get_customer(company_id: str, db: Session = Depends(get_db)):
    detail = customer_service.get_customer_detail(company_id, db)
    if not detail:
        raise HTTPException(
            status_code=404,
            detail={"code": "COMPANY_NOT_FOUND", "detail": f"Company {company_id} was not found."},
        )
    return detail

# 3. KULLANIM TRENDİ (DETAY SAYFASI GRAFİĞİ)
# DÜZELTME: Path 'usage-trend' yerine 'usage' yapıldı (api.js ile tam uyum)
@router.get("/{company_id}/usage", response_model=UsageTrendResponse)
def usage_trend(company_id: str, db: Session = Depends(get_db)):
    exists = db.query(models.Customer).filter(models.Customer.company_id == company_id).first()
    if not exists:
        raise HTTPException(
            status_code=404,
            detail={"code": "COMPANY_NOT_FOUND", "detail": f"Company {company_id} was not found."},
        )
    return customer_service.get_usage_trend(company_id, db)

# 4. XAI (SHAP) ANALİZİ (DETAY SAYFASI BAR CHART)
@router.get("/{company_id}/xai", response_model=XAIResponse)
def get_xai(company_id: str, db: Session = Depends(get_db)):
    exists = db.query(models.Customer).filter(models.Customer.company_id == company_id).first()
    if not exists:
        raise HTTPException(
            status_code=404,
            detail={"code": "COMPANY_NOT_FOUND", "detail": f"Company {company_id} was not found."},
        )
    from app.services.xai_service import get_xai_explanation
    return get_xai_explanation(company_id, db)


# 5. XAI PDF RAPORU
@router.get("/{company_id}/report")
def download_xai_report(company_id: str, db: Session = Depends(get_db)):
    if not db.query(models.Customer).filter(models.Customer.company_id == company_id).first():
        raise HTTPException(status_code=404, detail=f"Company {company_id} was not found.")
    from app.services.pdf_service import generate_pdf
    try:
        pdf_bytes = generate_pdf(company_id, db)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {exc}")
    filename = f"rassay-xai-{company_id}-{datetime.now(timezone.utc).strftime('%Y%m%d')}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
