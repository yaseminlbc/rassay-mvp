"""
Risk score ve level kuralları — Rehber Bölüm 6 & 10
"""
from app.services.prediction_service import classify_risk_level, calculate_risk_score


def test_risk_score_high_above_75():
    assert classify_risk_level(76) == "High"
    assert classify_risk_level(100) == "High"
    assert classify_risk_level(75.1) == "High"


def test_risk_score_medium_40_to_75():
    assert classify_risk_level(75) == "Medium"
    assert classify_risk_level(40) == "Medium"
    assert classify_risk_level(55) == "Medium"


def test_risk_score_low_below_40():
    assert classify_risk_level(39.9) == "Low"
    assert classify_risk_level(0) == "Low"


def test_risk_score_0_to_100_range():
    """Score asla 0-100 dışına çıkmamalı."""
    extreme_high = calculate_risk_score({
        "login_drop_pct": 9999,
        "active_user_drop_pct": 9999,
        "support_ticket_count": 9999,
        "renewal_days": 0,
    })
    assert 0 <= extreme_high <= 100

    extreme_low = calculate_risk_score({
        "login_drop_pct": 0,
        "active_user_drop_pct": 0,
        "support_ticket_count": 0,
        "renewal_days": 365,
    })
    assert 0 <= extreme_low <= 100


def test_high_risk_customer_via_api(client):
    resp = client.get("/api/customers/1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["risk_score"] > 75
    assert data["risk_level"] == "High"


def test_dashboard_summary_200(client):
    resp = client.get("/api/dashboard/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert 0 <= data["overall_health_score"] <= 100
    assert "high_risk_count" in data
    assert "total_active_accounts" in data


def test_risk_trend_200(client):
    resp = client.get("/api/dashboard/risk-trend?range=30d")
    assert resp.status_code == 200
    data = resp.json()
    assert data["range"] == "30d"
    assert len(data["points"]) > 0
