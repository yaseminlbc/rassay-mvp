from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ChurnPrediction

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


class ChurnOutcomePayload(BaseModel):
    company_id: str
    actual_outcome: int = Field(..., ge=0, le=1, description="1 = churned, 0 = retained")


def _run_retraining() -> None:
    """Background worker: retrain XGBoost on updated outcome labels."""
    try:
        from train_and_predict import run_churn_pipeline  # imported lazily — heavy deps
        run_churn_pipeline()
    except Exception as exc:
        # Background tasks cannot surface errors to the client; log and continue.
        print(f"[webhook] Retraining failed: {exc}")


@router.post("/churn-outcome", status_code=202)
def record_churn_outcome(
    payload: ChurnOutcomePayload,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Record a confirmed churn/retention outcome for a customer and schedule
    an asynchronous model retraining run.
    """
    pred = (
        db.query(ChurnPrediction)
        .filter(ChurnPrediction.company_id == payload.company_id)
        .order_by(ChurnPrediction.calculation_date.desc())
        .first()
    )
    if not pred:
        raise HTTPException(
            status_code=404,
            detail=f"No prediction found for company '{payload.company_id}'.",
        )

    pred.actual_outcome = payload.actual_outcome
    db.commit()

    background_tasks.add_task(_run_retraining)

    return {
        "status": "accepted",
        "company_id": payload.company_id,
        "actual_outcome": payload.actual_outcome,
        "message": "Outcome recorded. Model retraining queued in the background.",
    }
