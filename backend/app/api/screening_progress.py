from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.database import get_db
from app.models.resume_tables import Resume
from app.dto.screening_progress import ScreeningProgressResponse, ScreeningStep

router = APIRouter(prefix="/screening-progress", tags=["Screening Progress"])

STEP_NAMES = [
    "Extracting Text",
    "Extracting Skills",
    "Extracting Experience",
    "Matching with Job",
    "Calculating Score",
    "Generating Result",
]


@router.get("", response_model=ScreeningProgressResponse)
def get_screening_progress(db: Session = Depends(get_db)):
    # Fetch the most recently uploaded resume from DB
    latest_resume = db.query(Resume).order_by(desc(Resume.created_at)).first()

    if not latest_resume:
        raise HTTPException(status_code=404, detail="No resume found. Please upload a resume first.")


    steps = [ScreeningStep(name=name, status="pending") for name in STEP_NAMES]

    return ScreeningProgressResponse(
        steps=steps,
        progress_percentage=0,
        status_message="Waiting to start processing"
    )