
import pytest
import tempfile
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Geçici DB dosyası oluştur
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
TEST_DB_PATH = _tmp.name
_tmp.close()
TEST_DB_URL = f"sqlite:///{TEST_DB_PATH}"

engine_test = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
SessionTest = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

# App import öncesi engine'i patch et
import app.database as db_module
db_module.engine = engine_test
db_module.SessionLocal = SessionTest

from app.database import Base, get_db
from app.main import app
from app import models

def override_get_db():
    db = SessionTest()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)
    os.unlink(TEST_DB_PATH)

@pytest.fixture(scope="session")
def db(setup_db):
    session = SessionTest()
    yield session
    session.close()

@pytest.fixture(scope="session", autouse=True)
def seed_test_data(db, setup_db):
    now = datetime.now() # utcnow yerine now kullanmak daha sağlıklıdır

    # DÜZELTME: models.Company -> models.Customer
    # Not: Eğer models.py içinde name alanı company_name ise burayı company_name=... olarak değiştir
    c1 = models.Customer(company_id=1, name="HighRisk Corp",  industry="Tech",    account_owner="Alice", join_date=(now - timedelta(days=400)).date())
    c2 = models.Customer(company_id=2, name="MediumRisk LLC", industry="Finance", account_owner="Bob",   join_date=(now - timedelta(days=200)).date())
    c3 = models.Customer(company_id=3, name="LowRisk Inc",    industry="SaaS",    account_owner="Carol", join_date=(now - timedelta(days=300)).date())
    c4 = models.Customer(company_id=4, name="NewAccount Co",  industry="Startup", account_owner="Dave",  join_date=(now - timedelta(days=20)).date())
    for c in [c1, c2, c3, c4]:
        db.add(c)
    db.flush()

    db.add(models.Subscription(company_id=1, plan_type="Enterprise", monthly_fee=4800))
    db.add(models.Subscription(company_id=2, plan_type="Growth",     monthly_fee=800))
    db.add(models.Subscription(company_id=3, plan_type="Startup",    monthly_fee=200))
    db.add(models.Subscription(company_id=4, plan_type="Startup",    monthly_fee=150))
    db.flush()

    # HighRisk: son 14 günde login dramatik düşüş
    for i in range(90):
        day = now - timedelta(days=90 - i)
        login = 3 if i >= 76 else 20
        db.add(models.UsageData(company_id=1, timestamp=day, login_count=login, active_users=1, feature_usage_count=2, support_ticket_count=5))
    
    # MediumRisk: orta düşüş
    for i in range(60):
        day = now - timedelta(days=60 - i)
        login = 12 if i >= 46 else 25
        db.add(models.UsageData(company_id=2, timestamp=day, login_count=login, active_users=5, feature_usage_count=12, support_ticket_count=2))
    
    # LowRisk: sağlıklı
    for i in range(90):
        db.add(models.UsageData(company_id=3, timestamp=now - timedelta(days=90-i), login_count=80, active_users=25, feature_usage_count=50, support_ticket_count=0))
    
    # NewAccount: 20 gün (insufficient data)
    for i in range(20):
        db.add(models.UsageData(company_id=4, timestamp=now - timedelta(days=20-i), login_count=40, active_users=10, feature_usage_count=20, support_ticket_count=0))
    db.flush()

    db.add(models.ChurnPrediction(prediction_id=1, company_id=1, risk_score=88.0, risk_level="High",   top_risk_factor="Decreased Login Frequency", calculation_date=now))
    db.add(models.ChurnPrediction(prediction_id=2, company_id=2, risk_score=55.0, risk_level="Medium", top_risk_factor="Active User Drop",          calculation_date=now))
    db.add(models.ChurnPrediction(prediction_id=3, company_id=3, risk_score=15.0, risk_level="Low",    top_risk_factor="N/A",                       calculation_date=now))
    db.add(models.ChurnPrediction(prediction_id=4, company_id=4, risk_score=80.0, risk_level="High",   top_risk_factor="Insufficient data",         calculation_date=now))
    db.flush()

    for feat, impact, level in [
        ("Decreased Login Frequency",      0.42, "High"),
        ("Low Core Feature Usage",         0.31, "Medium"),
        ("Support Ticket Volume Increase", 0.18, "Medium"),
    ]:
        db.add(models.XAIFactor(prediction_id=1, feature_name=feat, impact_value=impact, impact_level=level, direction="negative"))

    db.add(models.Alert(
        alert_id=1, company_id=1, prediction_id=1,
        message="Usage dropped 45%.",
        recommended_action="Schedule check-in",
        severity="High", status="open", created_at=now,
    ))
    db.commit()

@pytest.fixture(scope="session")
def client(setup_db, seed_test_data):
    from fastapi.testclient import TestClient
    return TestClient(app)
