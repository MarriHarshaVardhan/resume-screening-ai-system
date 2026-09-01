import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.resume_tables import Resume, Job, User
from app.ai.services.screening_agent import screening_agent
from app.ai.rag.kb_vector_engine import kb_engine
from app.dto.ai_screening import AIScreeningResponseDTO

logger = logging.getLogger(__name__)


def execute_ai_screening(
    db: Session,
    user: User,
    resume_id: int | None = None,
    job_id: int | None = None
) -> AIScreeningResponseDTO:
    """
    Execute AI RAG screening pipeline for user's uploaded resume against target job description.
    """
    if resume_id:
        resume = db.query(Resume).filter(Resume.resume_id == resume_id, Resume.user_id == user.user_id).first()
    else:
        resume = db.query(Resume).filter(Resume.user_id == user.user_id).order_by(Resume.created_at.desc()).first()

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume found for candidate. Please upload a resume first."
        )

    target_job_id = job_id
    if not target_job_id:
        job = db.query(Job).order_by(Job.created_at.desc()).first()
        if not job:
            job = Job(
                job_title="Software Engineer",
                job_description="Looking for Software Engineer with skills in Python, FastAPI, PostgreSQL, and Data Structures.",
                required_skills=["Python", "FastAPI", "PostgreSQL", "Data Structures"],
                required_experience="1+ years"
            )
            db.add(job)
            db.commit()
            db.refresh(job)
        target_job_id = job.job_id

    screening = screening_agent.screen_resume_against_job(
        db=db,
        resume_id=resume.resume_id,
        job_id=target_job_id
    )

    return AIScreeningResponseDTO(
        message="AI RAG Screening completed successfully",
        screening_id=screening.screening_id,
        candidate_name=user.name,
        job_title=screening.job.job_title if screening.job else "N/A",
        match_score=screening.match_score or 0.0,
        status=screening.status or "Completed",
        matched_skills=screening.matched_skills or [],
        missing_skills=screening.missing_skills or [],
        recommendation=screening.recommendation or ""
    )


def search_knowledge_base_rag(query: str, db: Session) -> dict:
    """
    Search indexed resume knowledge base using RAG vector similarity.
    """
    resumes = db.query(Resume).filter(Resume.resume_text.isnot(None)).all()
    results = []

    for r in resumes:
        text = r.cleaned_resume_text or r.resume_text or ""
        score = kb_engine.compute_similarity(query, text)
        if score > 0:
            user_name = r.user.name if r.user else "Unknown"
            results.append({
                "resume_id": r.resume_id,
                "candidate": user_name,
                "file_name": r.resume_file_name,
                "relevance_score": score,
                "matched_snippet": text[:200] + "..."
            })

    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    return {
        "query": query,
        "results": results[:5]
    }
