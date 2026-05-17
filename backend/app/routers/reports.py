import io

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.pdf_service import generate_pdf

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/pdf/{company_id}", summary="Download XAI churn risk PDF report")
def get_pdf_report(company_id: str, db: Session = Depends(get_db)):
    try:
        pdf_bytes = generate_pdf(company_id, db)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="rassay_report_{company_id}.pdf"'
        },
    )
