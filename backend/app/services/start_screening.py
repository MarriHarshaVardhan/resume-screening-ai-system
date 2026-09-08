import logging

from app.ai.agents.screening_agent import run_screening_agent
from app.dto.start_screening import StartScreeningDTO
from app.models.resume_tables import Job, Resume, ScreeningResult, User
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

def start_screening(data: StartScreeningDTO, current_user: User, db: Session):
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

    if not resume.cleaned_resume_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume text has not been cleaned"
        )

    job = Job(
        job_title=data.job_title.strip(),
        required_skills=data.required_skills
    )

    db.add(job)
    db.flush()

    screening = ScreeningResult(
        user_id=current_user.user_id,
        resume_id=resume.resume_id,
        job_id=job.job_id,
        status="PROCESSING",
        current_step="AI_SCREENING",
        progress=20
    )

    db.add(screening)
    db.flush()

    try:
        result = run_screening_agent(
            resume_text=resume.cleaned_resume_text,
            resume_id=resume.resume_id,
            job_title=job.job_title,
            required_skills=job.required_skills
        )

        matched_skills = result.get("matched_skills", [])
        missing_skills = result.get("missing_skills", [])
        match_score = float(result.get("match_score", 0))
        screening_result = result.get("screening_result", "REVIEW")
        recommendation = result.get("recommendation", "")
        experience_assessment = result.get("experience_assessment", "")
        qualification_assessment = result.get("qualification_assessment", "")
        strengths = result.get("strengths", [])
        concerns = result.get("concerns", [])
        score_breakdown = result.get("score_breakdown", {})

        if not isinstance(matched_skills, list):
            raise ValueError("Invalid matched_skills format")

        if not isinstance(missing_skills, list):
            raise ValueError("Invalid missing_skills format")

        if not isinstance(strengths, list):
            raise ValueError("Invalid strengths format")

        if not isinstance(concerns, list):
            raise ValueError("Invalid concerns format")

        if not isinstance(score_breakdown, dict):
            raise ValueError("Invalid score_breakdown format")

        if not 0 <= match_score <= 100:
            raise ValueError("Invalid match_score")

        if screening_result not in {"SHORTLISTED", "REJECTED", "REVIEW"}:
            raise ValueError("Invalid screening_result")

        screening.status = "COMPLETED"
        screening.current_step = "COMPLETED"
        screening.progress = 100
        screening.matched_skills = matched_skills
        screening.missing_skills = missing_skills
        screening.match_score = match_score
        screening.screening_result = screening_result
        screening.recommendation = recommendation
        screening.experience_assessment = experience_assessment
        screening.qualification_assessment = qualification_assessment
        screening.strengths = strengths
        screening.concerns = concerns
        screening.score_breakdown = score_breakdown

        db.commit()
        db.refresh(screening)

        logger.info(
            "Screening completed: screening_id=%s resume_id=%s job_id=%s",
            screening.screening_id,
            resume.resume_id,
            job.job_id
        )

        return {
            "screening_id": screening.screening_id,
            "resume_id": resume.resume_id,
            "job_id": job.job_id,
            "status": screening.status,
            "current_step": screening.current_step,
            "progress": screening.progress,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "match_score": match_score,
            "screening_result": screening_result,
            "recommendation": recommendation,
            "experience_assessment": experience_assessment,
            "qualification_assessment": qualification_assessment,
            "strengths": strengths,
            "concerns": concerns,
            "score_breakdown": score_breakdown
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        logger.exception("Screening failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Resume screening failed"
        )