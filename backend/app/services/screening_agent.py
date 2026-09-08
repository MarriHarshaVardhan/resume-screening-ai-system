import logging

from app.ai.agents.screening_agent import run_screening_agent
from app.dto.screening_agent import ScreeningAgentRequestDTO, ScreeningAgentResponseDTO
from app.models.resume_tables import Resume, User
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

def execute_screening_agent(
    data: ScreeningAgentRequestDTO,
    current_user: User,
    db: Session
):
    resume = db.query(Resume).filter(
        Resume.resume_id == data.resume_id,
        Resume.user_id == current_user.user_id,
        Resume.deleted_at.is_(None)
    ).first()

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    resume_text = resume.cleaned_resume_text or resume.resume_text

    if not resume_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume text is not available"
        )

    try:
        result = run_screening_agent(
            resume_text=resume_text,
            resume_id=resume.resume_id,
            job_title=data.job_title.strip()
        )

        return ScreeningAgentResponseDTO(
            resume_id=resume.resume_id,
            job_title=data.job_title.strip(),
            **result
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception:
        logger.exception(
            "Screening agent service failed: resume_id=%s",
            data.resume_id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Screening agent failed"
        )