import logging

from app.core.security import get_current_user
from app.dto.resume_cleaning import ResumeCleaningResponseDTO
from app.models.database import get_db
from app.models.resume_tables import User
from app.services.resume_cleaning import clean_resume_text_service
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/resume",
    tags=["Resume"]
)


@router.post(
    "/clean-text/{resume_id}",
    response_model=ResumeCleaningResponseDTO
)
def clean_resume_text_api(
    resume_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    )
):

    logger.info(
        "POST /resume/clean-text/%s called by user_id=%s",
        resume_id,
        current_user.user_id
    )

    return clean_resume_text_service(
        resume_id=resume_id,
        current_user=current_user,
        db=db
    )