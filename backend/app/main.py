from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import Base, engine, get_db
# Modellerin yüklenmesi için gerekli
import app.models 

# Router Importları
from app.dashboard import router as dashboard_router
from app.customers import router as customers_router
from app.misc import (
    alerts_router,
    integrations_router,
    reports_router,
    ingest_router,
    predictions_router,
)
from app.routers.data_import import router as import_router
from app.routers.auth import router as auth_router
from app.routers.command_center import router as command_center_router
from app.routers.reports import router as pdf_reports_router
from app.routers.webhooks import router as webhooks_router
from app.schemas import HealthResponse

# Tabloları oluştur
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="RASSAY Churn Prediction API",
    description="B2B SaaS müşteri churn tahmin ve XAI açıklama sistemi",
    version="1.0.0",
)

# CORS Ayarları - Konsoldaki kırmızı hataları bu blok çözer
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "http://localhost:3000" # Alternatif portlar için önlem
    ], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROUTER'LARIN SİSTEME BAĞLANMASI ---
# Not: Hepsinin başına /api/v1 ekliyoruz ki Frontend'deki api.js ile tam eşleşsin.
app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(customers_router, prefix="/api/v1")
app.include_router(alerts_router, prefix="/api/v1")
app.include_router(integrations_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")
app.include_router(ingest_router, prefix="/api/v1")
app.include_router(predictions_router, prefix="/api/v1")
app.include_router(import_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(command_center_router, prefix="/api/v1")
app.include_router(pdf_reports_router, prefix="/api/v1")
app.include_router(webhooks_router, prefix="/api/v1")

@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    return HealthResponse(status="ok", service="RASSAY API", version="1.0.0")

@app.get("/api/test-db", tags=["Health"])
def test_db_connection(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "success", "message": "🎉 RASSAY Veritabanı bağlantısı KUSURSUZ çalışıyor!"}
    except Exception as e:
        return {"status": "error", "message": f"❌ Bağlantı hatası: {str(e)}"}
    