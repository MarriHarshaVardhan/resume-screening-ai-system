import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.dto.resume_analysis import ResumeAnalysisResponseDTO
from app.models.database import get_db
from app.models.resume_tables import User
from app.services.resume_analysis import analyze_resume


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/resume",
    tags=["Resume"]
)


@router.post(
    "/analyze/{resume_id}/{job_id}",
    response_model=ResumeAnalysisResponseDTO
)
def analyze_resume_api(
    resume_id: int,
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    logger.info(
        "POST /resume/analyze/%s/%s called by user_id=%s",
        resume_id,
        job_id,
        current_user.user_id
    )

    return analyze_resume(
        resume_id=resume_id,
        job_id=job_id,
        current_user=current_user,
        db=db
    )


@router.get("/debug/{resume_id}/{job_id}")
def debug_analyze_api(
    resume_id: int,
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from app.models.resume_tables import Resume, Job

    resume = db.query(Resume).filter(
        Resume.resume_id == resume_id,
        Resume.user_id == current_user.user_id,
        Resume.deleted_at.is_(None)
    ).first()

    job = db.query(Job).filter(
        Job.job_id == job_id,
        Job.deleted_at.is_(None)
    ).first()

    return {
        "resume_exists": resume is not None,
        "resume_has_cleaned_text": resume.cleaned_resume_text is not None if resume else False,
        "resume_cleaned_text_preview": resume.cleaned_resume_text[:100] if resume and resume.cleaned_resume_text else None,
        "job_exists": job is not None,
        "job_title": job.job_title if job else None,
        "user_id": current_user.user_id
    }