import logging

from app.core.security import get_current_user
from app.dto.screening_agent import ScreeningAgentRequestDTO
from app.models.database import get_db
from app.models.resume_tables import User
from app.services.screening_agent import execute_screening_agent
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/screening-agent", tags=["Screening Agent"])

@router.post("/run")
def run_screening_agent_api(
    data: ScreeningAgentRequestDTO,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logger.info(
        "POST /screening-agent/run called by user_id=%s",
        current_user.user_id
    )

    return execute_screening_agent(
        data=data,
        current_user=current_user,
        db=db
    )