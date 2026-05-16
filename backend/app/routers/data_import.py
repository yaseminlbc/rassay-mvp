"""
Data Import pipeline endpoint.

POST /api/v1/import/upload
  - Accepts CSV or Excel file
  - Validates required columns
  - Runs XGBoost + SHAP on every row
  - Upserts Customer, ChurnPrediction, and XAIFactor records
  - Returns a processing summary
"""
import io
from datetime import datetime

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ChurnPrediction, Customer, XAIFactor
from app.services import xgboost_service

router = APIRouter(prefix="/import", tags=["import"])

REQUIRED_COLUMNS = {"company_id", "mrr_value", "plan_type"}


def _parse_file(file: UploadFile) -> pd.DataFrame:
    content = file.file.read()
    name = (file.filename or "").lower()
    if name.endswith(".csv"):
        return pd.read_csv(io.BytesIO(content), dtype={"company_id": str})
    if name.endswith((".xlsx", ".xls")):
        return pd.read_excel(io.BytesIO(content), dtype={"company_id": str})
    raise HTTPException(
        status_code=400,
        detail="Unsupported file type. Please upload a .csv, .xlsx, or .xls file.",
    )


@router.post("/upload")
async def upload_and_predict(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not xgboost_service.is_model_available():
        raise HTTPException(
            status_code=503,
            detail="XGBoost model not found. Run backend/train_and_predict.py first.",
        )

    # ── Parse file ────────────────────────────────────────────────────────────
    try:
        df = _parse_file(file)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not parse file: {e}")

    df.columns = [str(c).strip().lower() for c in df.columns]

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"Missing required columns: {sorted(missing)}. "
                   f"File has: {sorted(df.columns.tolist())}",
        )

    df = df.dropna(subset=["company_id"])
    df["company_id"] = df["company_id"].astype(str).str.strip()
    if df.empty:
        raise HTTPException(status_code=422, detail="File contains no valid rows.")

    # ── Pass 1: run model predictions (pure Python, no DB) ───────────────────
    records = []   # list of (row_series, prediction_dict)
    errors  = []

    for pos, (_, row) in enumerate(df.iterrows(), start=2):
        company_id = row["company_id"]
        try:
            features = {
                "mrr_value":          float(row.get("mrr_value") or 0),
                "account_age_months": int(float(row.get("account_age_months") or 0)),
                "support_tickets":    int(float(row.get("support_tickets") or 0)),
                "login_count":        int(float(row.get("login_count") or 0)),
                "plan_type":          str(row.get("plan_type") or ""),
            }
            prediction = xgboost_service.predict_single(features)
            records.append((company_id, row, features, prediction))
        except Exception as exc:
            errors.append(f"Row {pos} (company_id={company_id}): {exc}")

    # ── Pass 2: upsert to DB inside a single transaction ─────────────────────
    inserted = updated = high = medium = low = 0

    for company_id, row, features, pred in records:
        try:
            sp = db.begin_nested()  # savepoint: a single bad row won't kill the batch

            customer = db.query(Customer).filter(Customer.company_id == company_id).first()
            if customer is None:
                customer = Customer(company_id=company_id)
                db.add(customer)
                inserted += 1
            else:
                updated += 1

            customer.mrr_value          = features["mrr_value"]
            customer.plan_type          = features["plan_type"]
            customer.account_age_months = features["account_age_months"]
            customer.support_tickets    = features["support_tickets"]
            customer.login_count        = features["login_count"]
            customer.churn_probability  = pred["risk_score"]

            if "churn_status" in row and pd.notna(row.get("churn_status")):
                customer.churn_status = int(float(row["churn_status"]))

            db.flush()

            # Remove stale predictions / XAI for this company
            old_preds = (
                db.query(ChurnPrediction)
                .filter(ChurnPrediction.company_id == company_id)
                .all()
            )
            for old in old_preds:
                db.query(XAIFactor).filter(XAIFactor.prediction_id == old.prediction_id).delete()
                db.delete(old)

            db.flush()

            # Fresh prediction row
            churn_pred = ChurnPrediction(
                company_id=company_id,
                calculation_date=datetime.utcnow(),
                risk_score=pred["risk_score"],
                risk_level=pred["risk_level"],
                top_risk_factor=pred["top_risk_factor"],
                model_version="v2.0-xgboost-shap",
            )
            db.add(churn_pred)
            db.flush()

            # Top-3 SHAP factors
            for factor in pred["shap_factors"][:3]:
                db.add(XAIFactor(
                    prediction_id=churn_pred.prediction_id,
                    feature_name=factor["feature_name"],
                    impact_value=factor["impact_value"],
                    impact_level=factor["impact_level"],
                    direction=factor["direction"],
                ))

            sp.commit()

            if pred["risk_level"] == "High":
                high += 1
            elif pred["risk_level"] == "Medium":
                medium += 1
            else:
                low += 1

        except Exception as exc:
            sp.rollback()
            errors.append(f"DB error (company_id={company_id}): {exc}")
            if pred["risk_level"] == "High":   high -= 1 if high else 0
            elif pred["risk_level"] == "Medium": medium -= 1 if medium else 0

    db.commit()

    return {
        "status": "success",
        "total_processed": inserted + updated,
        "inserted": inserted,
        "updated": updated,
        "high_risk": high,
        "medium_risk": medium,
        "low_risk": low,
        "errors": len(errors),
        "error_details": errors[:20],
    }
