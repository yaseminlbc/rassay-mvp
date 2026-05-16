"""
API testleri — Rehber Bölüm 10
"""


def test_get_customers_200(client):
    resp = client.get("/api/customers")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_customers_sorted_by_risk_score_desc(client):
    resp = client.get("/api/customers")
    data = resp.json()
    scores = [c["risk_score"] for c in data if c["risk_score"] is not None]
    assert scores == sorted(scores, reverse=True)


def test_filter_high_risk(client):
    resp = client.get("/api/customers?risk_level=High")
    assert resp.status_code == 200
    for c in resp.json():
        assert c["risk_level"] == "High"


def test_filter_medium_risk(client):
    resp = client.get("/api/customers?risk_level=Medium")
    assert resp.status_code == 200
    for c in resp.json():
        assert c["risk_level"] == "Medium"


def test_filter_invalid_risk_level_400(client):
    resp = client.get("/api/customers?risk_level=INVALID")
    assert resp.status_code == 400


def test_search_filter(client):
    resp = client.get("/api/customers?search=HighRisk")
    assert resp.status_code == 200
    data = resp.json()
    assert any("HighRisk" in c["company_name"] for c in data)


def test_get_customer_detail_200(client):
    resp = client.get("/api/customers/1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["company_id"] == 1
    assert "risk_score" in data
    assert "plan_type" in data


def test_get_customer_not_found_404(client):
    resp = client.get("/api/customers/9999")
    assert resp.status_code == 404
    body = resp.json()
    assert body["detail"]["code"] == "COMPANY_NOT_FOUND"


def test_usage_trend_200(client):
    resp = client.get("/api/customers/1/usage-trend")
    assert resp.status_code == 200
    data = resp.json()
    assert "points" in data
    assert len(data["points"]) > 0


def test_usage_trend_not_found(client):
    resp = client.get("/api/customers/9999/usage-trend")
    assert resp.status_code == 404
