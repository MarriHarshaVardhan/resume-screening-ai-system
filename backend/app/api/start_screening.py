import logging

from app.core.security import get_current_user
from app.dto.start_screening import StartScreeningDTO, StartScreeningResponseDTO
from app.models.database import get_db
from app.models.resume_tables import User
from app.services.start_screening import start_screening
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/screening", tags=["Screening"])

@router.post("/start", response_model=StartScreeningResponseDTO)
def start_screening_api(
    data: StartScreeningDTO,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db)  # noqa: B008
):
    logger.info(
        "POST /screening/start called by user_id=%s resume_id=%s",
        current_user.user_id,
        data.resume_id
    )
    return start_screening(
        data=data,
        current_user=current_user,
        db=db
    )