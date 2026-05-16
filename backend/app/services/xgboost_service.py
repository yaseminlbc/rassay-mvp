"""
XGBoost inference service.

Loads the model and feature metadata produced by train_and_predict.py exactly
once (module-level singleton) and exposes predict_single() for single-customer
scoring + SHAP explanation.

Artefacts expected at backend/model/:
    xgb_churn.json        – trained XGBoost model
    feature_columns.json  – feature list saved during training (numeric + plan OHE)

Run train_and_predict.py at least once before calling this service.
"""
import json
from pathlib import Path
from typing import Optional
import numpy as np
import pandas as pd
import xgboost as xgb
import shap

_MODEL_DIR        = Path(__file__).parent.parent.parent / "model"
MODEL_PATH        = _MODEL_DIR / "xgb_churn.json"
FEATURE_META_PATH = _MODEL_DIR / "feature_columns.json"

# Singletons — populated on first _load() call
_model:        Optional[xgb.XGBClassifier]  = None
_explainer:    Optional[shap.TreeExplainer] = None
_feature_meta: Optional[dict]               = None


def is_model_available() -> bool:
    """True only when both model and feature metadata files exist."""
    return MODEL_PATH.exists() and FEATURE_META_PATH.exists()


def _label(f_key: str) -> str:
    """Convert a raw feature key to a human-readable display name."""
    base = {
        'mrr_value':          'Monthly Recurring Revenue',
        'account_age_months': 'Account Age (Months)',
        'support_tickets':    'Support Ticket Volume',
        'login_count':        'Login Frequency',
    }
    if f_key in base:
        return base[f_key]
    if f_key.startswith('plan_'):
        return f"Plan: {f_key[len('plan_'):]}"
    return f_key


def _load() -> tuple[xgb.XGBClassifier, shap.TreeExplainer, dict]:
    """Load model, explainer, and feature metadata from disk; cache for reuse."""
    global _model, _explainer, _feature_meta
    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"XGBoost model not found at {MODEL_PATH}. "
                "Run backend/train_and_predict.py first."
            )
        if not FEATURE_META_PATH.exists():
            raise FileNotFoundError(
                f"Feature metadata not found at {FEATURE_META_PATH}. "
                "Run backend/train_and_predict.py first."
            )
        _model = xgb.XGBClassifier()
        _model.load_model(str(MODEL_PATH))
        _explainer = shap.TreeExplainer(_model)
        with open(FEATURE_META_PATH) as f:
            _feature_meta = json.load(f)
    return _model, _explainer, _feature_meta


def _shap_row(shap_values, idx: int = 0) -> np.ndarray:
    """Handle both old (list) and new (2-D ndarray) SHAP APIs."""
    if isinstance(shap_values, list):
        return np.asarray(shap_values[1])[idx]
    return np.asarray(shap_values)[idx]


def predict_single(feature_values: dict) -> dict:
    """
    Score one customer and return SHAP-based XAI factors.

    Args:
        feature_values: dict containing numeric fields plus 'plan_type' (raw string,
                        e.g. 'Month-to-month').  Missing keys default to 0 / unknown.

    Returns:
        risk_score      – float in [0, 1] (store directly in ChurnPrediction.risk_score)
        risk_level      – "High" | "Medium" | "Low"
        top_risk_factor – human-readable label of the highest-impact SHAP feature
        shap_factors    – list[dict] sorted by abs(impact_value) descending
    """
    model, explainer, meta = _load()

    # ── Build the feature row in the exact order the model was trained on ──────
    numeric_features  = meta['numeric_features']
    plan_type_columns = meta['plan_type_columns']
    all_features      = meta['all_features']

    row: dict[str, float] = {}

    # Numeric features
    for f in numeric_features:
        row[f] = float(feature_values.get(f) or 0)

    # One-hot encode plan_type: match "plan_<value>" columns
    plan_type = str(feature_values.get('plan_type') or '')
    for col in plan_type_columns:
        # col is e.g. "plan_Month-to-month"; strip the "plan_" prefix to compare
        row[col] = 1.0 if plan_type == col[len('plan_'):] else 0.0

    X = pd.DataFrame([[row.get(f, 0.0) for f in all_features]], columns=all_features)

    # ── Inference ─────────────────────────────────────────────────────────────
    prob = float(model.predict_proba(X)[0, 1])

    if prob > 0.70:    risk_level = "High"
    elif prob >= 0.40: risk_level = "Medium"
    else:              risk_level = "Low"

    raw_shap = explainer.shap_values(X)
    row_shap = _shap_row(raw_shap, idx=0)

    # ── Build factor list from all features ───────────────────────────────────
    factors = []
    for f_key, f_val in zip(all_features, row_shap):
        f_val   = float(f_val)
        abs_val = abs(f_val)
        factors.append({
            "feature_name": _label(f_key),
            "impact_value": round(f_val, 4),
            "impact_level": (
                "High"   if abs_val > 0.5  else
                "Medium" if abs_val > 0.2  else
                "Low"
            ),
            # SHAP > 0 pushes toward churn (bad) → "Negative" for customer health
            "direction": "Negative" if f_val > 0 else "Positive",
        })

    factors.sort(key=lambda x: abs(x["impact_value"]), reverse=True)

    return {
        "risk_score":      round(prob, 4),
        "risk_level":      risk_level,
        "top_risk_factor": factors[0]["feature_name"] if factors else "Insufficient data",
        "shap_factors":    factors,
    }
