import logging
from fastapi import APIRouter, Depends, File, Form, UploadFile
from app.core.security import get_current_user
from app.models.resume_tables import User
from app.services.knowledge_upload import upload_knowledge

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/knowledge", tags=["Knowledge"])

@router.post("/upload")
def upload_knowledge_api(
    file: UploadFile = File(...),
    job_title: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    logger.info(
        "POST /knowledge/upload called by user_id=%s",
        current_user.user_id
    )
    return upload_knowledge(
        file=file,
        job_title=job_title,
        current_user=current_user
    )