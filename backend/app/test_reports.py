"""
CSV export + alerts + integrations testleri — Rehber Bölüm 10
"""


def test_csv_export_content_type(client):
    resp = client.get("/api/reports/churn-risk.csv")
    assert resp.status_code == 200
    assert "text/csv" in resp.headers["content-type"]


def test_csv_export_has_correct_columns(client):
    resp = client.get("/api/reports/churn-risk.csv")
    first_line = resp.text.splitlines()[0]
    assert "company_id" in first_line
    assert "risk_score" in first_line
    assert "risk_level" in first_line


def test_csv_export_has_rows(client):
    resp = client.get("/api/reports/churn-risk.csv")
    lines = [l for l in resp.text.splitlines() if l.strip()]
    assert len(lines) > 1   # header + en az 1 satır


def test_alerts_200(client):
    resp = client.get("/api/alerts")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0
    first = data[0]
    assert "alert_id" in first
    assert "company_name" in first
    assert "recommended_action" in first


def test_integrations_status_200(client):
    resp = client.get("/api/integrations/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["api_connection"] == "Active"
    assert "database" in data


def test_health_200(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
