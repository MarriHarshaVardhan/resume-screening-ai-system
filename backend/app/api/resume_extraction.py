import logging

from app.core.security import get_current_user
from app.dto.resume_extraction import ResumeExtractionResponseDTO
from app.models.database import get_db
from app.models.resume_tables import User
from app.services.resume_extraction import extract_resume_text
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/resume",
    tags=["Resume"]
)


@router.post(
    "/extract-text/{resume_id}",
    response_model=ResumeExtractionResponseDTO
)
def extract_resume_text_api(
    resume_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    )
):

    logger.info(
        "POST /resume/extract-text/%s called by user_id=%s",
        resume_id,
        current_user.user_id
    )

    return extract_resume_text(
        resume_id=resume_id,
        current_user=current_user,
        db=db
    )