# RASSAY Backend API

🚀 **[Canlı Yayını Görüntüle / Live Demo](https://rassay-mvp.vercel.app)**

FastAPI + SQLAlchemy + XGBoost/Mock ML + SHAP/XAI

## Hızlı Başlangıç

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# .env ayarla (SQLite default, PostgreSQL için DATABASE_URL değiştir)
cp .env.example .env

# Demo veriyi yükle
python app/seed.py

# Sunucuyu başlat
uvicorn app.main:app --reload --port 8000
```

Swagger UI: http://localhost:8000/docs

## Endpointler (frontend sözleşmesi)

| Method | URL | Açıklama |
|--------|-----|----------|
| GET | /api/health | Sağlık kontrolü |
| GET | /api/dashboard/summary | KPI özeti |
| GET | /api/dashboard/risk-trend?range=30d | Risk trend grafiği |
| GET | /api/customers | Müşteri listesi (risk_level, search filtresi) |
| GET | /api/customers/{id} | Müşteri detayı |
| GET | /api/customers/{id}/usage-trend | Kullanım trendi |
| GET | /api/customers/{id}/xai | XAI açıklaması |
| GET | /api/alerts | Uyarılar |
| GET | /api/integrations/status | Entegrasyon durumu |
| POST | /api/ingest/usage-data | Telemetry verisi ekle |
| POST | /api/predict/run | Tüm tahminleri yenile |
| GET | /api/reports/churn-risk.csv | CSV export |

## Frontend Entegrasyonu

Frontend `.env` dosyasına ekle:
```
VITE_API_BASE_URL=http://localhost:8000/api
```

CORS: `localhost:5173` (Vite) otomatik izinli.

## Testler

```bash
pytest tests/ -v
# 28 test, tümü geçmeli
```

Test çıktısı: `test_results/pytest_output.txt`

## PostgreSQL'e Geçiş

`.env` dosyasını güncelle:
```
DATABASE_URL=postgresql://user:password@localhost:5432/rassay
```
Kod değişikliği gerekmez.

## Risk Kuralları

- `risk_score > 75` → **High**
- `40 <= risk_score <= 75` → **Medium**  
- `risk_score < 40` → **Low**
- XAI sadece High risk + 30+ gün veri olan hesaplar için üretilir
