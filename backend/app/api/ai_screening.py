import logging
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.models.database import get_db
from app.models.resume_tables import User
from app.dto.ai_screening import AIScreeningRequestDTO, AIScreeningResponseDTO
from app.services.ai_screening import execute_ai_screening, search_knowledge_base_rag

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/ai",
    tags=["AI Screening Agent"]
)


@router.post("/screen", response_model=AIScreeningResponseDTO, include_in_schema=False)
def screen_resume_api(
    payload: AIScreeningRequestDTO,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Run AI RAG screening pipeline for a specific resume against a target job description.
    """
    return execute_ai_screening(
        db=db,
        user=current_user,
        resume_id=payload.resume_id,
        job_id=payload.job_id
    )


@router.post("/screen-latest", response_model=AIScreeningResponseDTO)
def screen_latest_resume_api(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Automatically process and AI screen candidate's latest uploaded resume.
    """
    return execute_ai_screening(
        db=db,
        user=current_user,
        resume_id=None,
        job_id=None
    )


@router.get("/kb/search", include_in_schema=False)
def search_kb_api(
    query: str = Query(..., description="Query terms or skills"),
    db: Session = Depends(get_db)
):
    """
    Search Knowledge Base resumes using RAG vector similarity (Internal API).
    """
    return search_knowledge_base_rag(query=query, db=db)
