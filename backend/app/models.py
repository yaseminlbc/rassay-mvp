from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(String, unique=True, index=True) # Integer yerine String yaptık
    mrr_value = Column(Float, nullable=False)
    plan_type = Column(String, nullable=False)
    account_age_months = Column(Integer, default=0)
    support_tickets = Column(Integer, default=0)
    login_count = Column(Integer, default=0)
    churn_status = Column(Integer, default=0)
    churn_probability = Column(Float, nullable=True)

class ChurnPrediction(Base):
    __tablename__ = "churn_predictions"

    prediction_id = Column(Integer, primary_key=True, index=True)
    company_id = Column(String, index=True)
    calculation_date = Column(DateTime, default=datetime.utcnow)
    risk_score = Column(Float)
    risk_level = Column(String(20), nullable=True)
    top_risk_factor = Column(String(255), nullable=True)
    model_version = Column(String(50), nullable=True)
    actual_outcome = Column(Integer, nullable=True)  # 1=churned, 0=retained

class XAIFactor(Base):
    __tablename__ = "xai_factors"
    
    factor_id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, index=True) # Müşteri id'si veya tahmin id'si
    feature_name = Column(String(255))
    impact_value = Column(Float)
    impact_level = Column(String(20))
    direction = Column(String(10))

class Alert(Base):
    __tablename__ = "alerts"

    alert_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_id = Column(String, index=True)
    prediction_id = Column(Integer, nullable=True)
    message = Column(String)
    recommended_action = Column(String, nullable=True)
    severity = Column(String)  # High, Medium, Low vb.
    status = Column(String, default="open")
    created_at = Column(DateTime, default=datetime.now)

class UsageData(Base):
    __tablename__ = "usage_data"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_id = Column(String, ForeignKey("customers.company_id"))
    login_count = Column(Integer, default=0)
    active_users = Column(Integer, default=0)
    feature_usage_count = Column(Integer, default=0)
    support_ticket_count = Column(Integer, default=0)
    nps_score = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.now)

