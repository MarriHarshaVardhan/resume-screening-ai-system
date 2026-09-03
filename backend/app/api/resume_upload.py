import logging

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    Depends
)

from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.models.database import get_db
from app.models.resume_tables import User
from app.dto.resume_upload import ResumeUploadResponseDTO
from app.services.resume_upload import upload_resume


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/resume",
    tags=["Resume"]
)


@router.post(
    "/upload",
    response_model=ResumeUploadResponseDTO
)
def upload_resume_api(
    file: UploadFile = File(...),

    job_title: str = Form(...),

    required_skills: str = Form(...),

    current_user: User = Depends(get_current_user),

    db: Session = Depends(get_db)
):

    logger.info(
        "POST /resume/upload called by user_id=%s",
        current_user.user_id
    )

    return upload_resume(
        file=file,
        job_title=job_title,
        required_skills=required_skills,
        current_user=current_user,
        db=db
    )