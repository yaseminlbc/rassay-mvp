from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# ==========================================
# 1. SAĞLIK VE GENEL YANIT ŞEMALARI
# ==========================================
class HealthResponse(BaseModel):
    status: str
    service: str
    version: str

class ErrorResponse(BaseModel):
    detail: str

# ==========================================
# 2. DASHBOARD VE TREND ŞEMALARI
# ==========================================
class RiskTrendPoint(BaseModel):
    period: str  # 'date' yerine 'period' yapalım, Frontend böyle bekliyor
    high: int
    medium: int
    low: int

class RiskTrendResponse(BaseModel):
    trends: List[RiskTrendPoint] = []

class DashboardSummary(BaseModel):
    total_clients: int = 0
    high_risk_count: int = 0
    medium_risk_count: int = 0 # Eklendi
    low_risk_count: int = 0    # Eklendi
    revenue_at_risk: float = 0.0 # Eklendi
    average_health_score: float = 0.0
    last_sync: str = "Just now"  # Eklendi

# ==========================================
# 3. MÜŞTERİ VE KULLANIM ŞEMALARI
# ==========================================
class CustomerListItem(BaseModel):
    id: Optional[int] = None
    company_id: str  # String ID uyumu
    company_name: str
    plan_type: Optional[str] = "Standard"
    risk_score: Optional[float] = 0.0
    risk_level: Optional[str] = "Low"
    top_risk_factor: Optional[str] = "None"
    account_owner: Optional[str] = "Unassigned"
    churn_status: Optional[int] = 0

    class Config:
        from_attributes = True
        populate_by_name = True

class CustomerDetail(BaseModel):
    id: int
    company_id: str # int -> str yapıldı
    account_age_months: Optional[int] = None
    mrr_value: Optional[float] = None
    support_tickets: Optional[int] = None
    login_count: Optional[int] = None
    churn_status: Optional[int] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UsagePoint(BaseModel):
    label: str
    value: float

class UsageTrendResponse(BaseModel):
    points: List[UsagePoint] = []

# ==========================================
# 4. ALERTLER, RAPORLAR VE ENTEGRASYONLAR
# ==========================================
class AlertItem(BaseModel):
    alert_id: int
    company_id: str # int -> str yapıldı (KRİTİK)
    company_name: str
    risk_score: Optional[float] = None
    severity: str
    message: str
    recommended_action: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class ReportItem(BaseModel):
    id: int
    report_name: str
    created_at: datetime
    file_path: str
    
    class Config:
        from_attributes = True

class IntegrationStatus(BaseModel):
    id: int
    name: str
    status: str
    last_sync: Optional[datetime] = None

# ==========================================
# 5. CHURN VE XAI ŞEMALARI
# ==========================================
class XAIFactor(BaseModel):
    feature_name: str
    impact_value: float
    impact_level: str
    # direction alanı modellerde yoksa Optional yapabiliriz
    direction: Optional[str] = "N/A" 
    
    class Config:
        from_attributes = True

class XAIResponse(BaseModel):
    prediction_id: int
    factors: List[XAIFactor]
    
    class Config:
        from_attributes = True

class ChurnRiskResponse(BaseModel):
    prediction_id: int
    company_id: str # int -> str yapıldı (KRİTİK)
    risk_score: float
    risk_level: Optional[str] = None
    top_risk_factor: Optional[str] = None
    model_version: Optional[str] = None
    calculation_date: datetime
    
    class Config:
        from_attributes = True

# Misc ve yardımcı şemalar
class IngestResponse(BaseModel):
    status: str
    records_processed: int
    message: str

class PredictRunResponse(BaseModel):
    job_id: str
    status: str
    started_at: datetime

class UsageDataIngest(BaseModel):
    company_id: str # int -> str yapıldı
    month: str
    usage_value: float

# Yedek takma isimler (Aliasing)
class XAIFactorResponse(XAIFactor): pass
class AlertResponse(AlertItem): pass
class ReportResponse(ReportItem): pass
class IntegrationResponse(IntegrationStatus): pass