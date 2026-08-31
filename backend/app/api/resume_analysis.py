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
    "/analyze/{resume_id}",
    response_model=ResumeAnalysisResponseDTO
)
def analyze_resume_api(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logger.info(
        "POST /resume/analyze/%s called by user_id=%s",
        resume_id,
        current_user.user_id
    )

    return analyze_resume(
        resume_id=resume_id,
        current_user=current_user,
        db=db
    )