"""
Training pipeline: reads customers from PostgreSQL, trains XGBoost with
plan_type one-hot encoding, saves the model + feature metadata to disk,
then pre-populates churn_predictions and xai_factors for every customer.

Run from backend/:
    python train_and_predict.py
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import xgboost as xgb
import shap
from datetime import datetime
from app.database import engine, SessionLocal
from app.models import ChurnPrediction, XAIFactor

NUMERIC_FEATURES = ['mrr_value', 'account_age_months', 'support_tickets', 'login_count']

MODEL_DIR         = Path(__file__).parent / "model"
MODEL_PATH        = MODEL_DIR / "xgb_churn.json"
FEATURE_META_PATH = MODEL_DIR / "feature_columns.json"

# Human-readable labels for numeric features and dynamically-named plan columns
_BASE_LABELS = {
    'mrr_value':          'Monthly Recurring Revenue',
    'account_age_months': 'Account Age (Months)',
    'support_tickets':    'Support Ticket Volume',
    'login_count':        'Login Frequency',
}


def _label(f_key: str) -> str:
    if f_key in _BASE_LABELS:
        return _BASE_LABELS[f_key]
    if f_key.startswith('plan_'):
        return f"Plan: {f_key[len('plan_'):]}"
    return f_key


def _risk_level(prob: float) -> str:
    if prob > 0.70:   return "High"
    if prob >= 0.40:  return "Medium"
    return "Low"


def _shap_row(shap_values, i: int) -> np.ndarray:
    """Handle both old (list) and new (2-D array) SHAP APIs."""
    if isinstance(shap_values, list):
        return np.asarray(shap_values[1])[i]
    return np.asarray(shap_values)[i]


def run_churn_pipeline():
    db = SessionLocal()

    print("1. Fetching customer data from database...")
    df = pd.read_sql("SELECT * FROM customers", engine)

    if df.empty:
        print("Error: No customers found in the database. Run seed.py first.")
        return

    print(f"   {len(df):,} customers loaded.")

    print("2. Encoding features (numeric + plan_type one-hot)...")
    df_enc   = pd.get_dummies(df, columns=['plan_type'], prefix='plan')
    plan_cols = sorted(c for c in df_enc.columns if c.startswith('plan_'))
    all_features = NUMERIC_FEATURES + plan_cols

    X = df_enc[all_features].fillna(0).astype(float)
    y = df['churn_status']

    print(f"   Feature matrix: {X.shape[1]} features — "
          f"{len(NUMERIC_FEATURES)} numeric + {len(plan_cols)} plan-type columns.")

    print("3. Training XGBoost model...")
    model = xgb.XGBClassifier(
        objective='binary:logistic',
        eval_metric='logloss',
        random_state=42,
    )
    model.fit(X, y)

    print(f"4. Saving model and feature metadata to {MODEL_DIR} ...")
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model.save_model(str(MODEL_PATH))

    feature_meta = {
        "numeric_features":  NUMERIC_FEATURES,
        "plan_type_columns": plan_cols,
        "all_features":      all_features,
    }
    with open(FEATURE_META_PATH, 'w') as f:
        json.dump(feature_meta, f, indent=2)
    print("   Saved xgb_churn.json + feature_columns.json.")

    print("5. Computing SHAP values for all customers...")
    explainer = shap.TreeExplainer(model)
    shap_vals = explainer.shap_values(X)
    proba     = model.predict_proba(X)[:, 1]

    print("6. Persisting predictions and XAI factors...")
    try:
        # Clear previous run's predictions and XAI rows before inserting fresh ones
        db.execute(__import__('sqlalchemy').text("DELETE FROM xai_factors"))
        db.execute(__import__('sqlalchemy').text("DELETE FROM churn_predictions"))
        db.commit()

        batch_size = 500
        for i, row in df.iterrows():
            prob     = float(proba[i])
            risk_lvl = _risk_level(prob)

            pred = ChurnPrediction(
                company_id=str(row['company_id']),
                risk_score=round(prob, 4),
                risk_level=risk_lvl,
                calculation_date=datetime.now(),
                model_version="v2.0-xgboost-shap",
            )
            db.add(pred)
            db.flush()  # need prediction_id before XAI rows

            row_shap    = _shap_row(shap_vals, i)
            named_shap  = list(zip(all_features, row_shap))
            top_factors = sorted(named_shap, key=lambda x: abs(x[1]), reverse=True)[:3]

            # Back-fill the top factor label now that we have the sorted SHAP list
            if top_factors:
                pred.top_risk_factor = _label(top_factors[0][0])

            for f_key, f_val in top_factors:
                f_val = float(f_val)
                db.add(XAIFactor(
                    prediction_id=pred.prediction_id,
                    feature_name=_label(f_key),
                    impact_value=round(f_val, 4),
                    impact_level=(
                        "High"   if abs(f_val) > 0.5  else
                        "Medium" if abs(f_val) > 0.2  else
                        "Low"
                    ),
                    direction="Negative" if f_val > 0 else "Positive",
                ))

            # Commit in batches to avoid holding a huge transaction
            if (i + 1) % batch_size == 0:
                db.commit()
                print(f"   ... {i + 1:,} / {len(df):,} committed")

        db.commit()  # flush remainder
        print(f"\nDone. Predictions + XAI factors saved for {len(df):,} customers.")

    except Exception as exc:
        print(f"Error during save: {exc}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_churn_pipeline()
