"""
XAI explanation service.

Serving strategy (in priority order):
  1. Return SHAP factors already persisted in xai_factors by a previous
     /predict/run call — zero inference cost, fastest path.
  2. If no DB rows exist but the trained model is on disk, compute live SHAP
     values for the customer's current feature snapshot and return them without
     persisting (so the response is still correct even before the batch job runs).
  3. If neither is available, return an empty factors list — the frontend
     Error Boundary handles the empty state gracefully.
"""
from sqlalchemy.orm import Session
from app import models
from app.schemas import XAIFactor as XAIFactorSchema, XAIResponse
from app.services import prediction_service


def get_xai_explanation(company_id: str, db: Session) -> XAIResponse:
    customer = (
        db.query(models.Customer)
        .filter(models.Customer.company_id == company_id)
        .first()
    )
    if not customer:
        return XAIResponse(prediction_id=0, factors=[])

    pred = prediction_service.get_latest_prediction(company_id, db)

    # ── Tier 1: serve from DB ─────────────────────────────────────────────────
    if pred:
        db_factors = (
            db.query(models.XAIFactor)
            .filter(models.XAIFactor.prediction_id == pred.prediction_id)
            .all()
        )
        if db_factors:
            db_factors.sort(key=lambda f: abs(f.impact_value), reverse=True)
            return XAIResponse(
                prediction_id=pred.prediction_id,
                factors=[
                    XAIFactorSchema(
                        feature_name=f.feature_name,
                        impact_value=f.impact_value,
                        impact_level=f.impact_level,
                        direction=f.direction if f.direction else (
                            "Negative" if f.impact_value > 0 else "Positive"
                        ),
                    )
                    for f in db_factors
                ],
            )

    # ── Tier 2: live SHAP computation ─────────────────────────────────────────
    from app.services import xgboost_service
    if xgboost_service.is_model_available():
        feature_values = {
            'mrr_value':          float(customer.mrr_value or 0),
            'account_age_months': int(customer.account_age_months or 0),
            'support_tickets':    int(customer.support_tickets or 0),
            'login_count':        int(customer.login_count or 0),
            'plan_type':          str(customer.plan_type or ''),
        }
        result = xgboost_service.predict_single(feature_values)
        return XAIResponse(
            prediction_id=pred.prediction_id if pred else 0,
            factors=[
                XAIFactorSchema(**f) for f in result['shap_factors'][:3]
            ],
        )

    # ── Tier 3: empty — frontend Error Boundary handles this ─────────────────
    return XAIResponse(prediction_id=pred.prediction_id if pred else 0, factors=[])
