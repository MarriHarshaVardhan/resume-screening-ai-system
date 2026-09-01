import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.ai.services.resume_analyzer import analyze_resume_with_groq
from app.models.resume_tables import Resume, User


logger = logging.getLogger(__name__)


def analyze_resume(
    resume_id: int,
    current_user: User,
    db: Session
):
    logger.info(
        "Resume analysis started: resume_id=%s, user_id=%s",
        resume_id,
        current_user.user_id
    )

    resume = (
        db.query(Resume)
        .filter(
            Resume.resume_id == resume_id,
            Resume.user_id == current_user.user_id,
            Resume.deleted_at.is_(None)
        )
        .first()
    )

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    if not resume.cleaned_resume_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume text is not cleaned. Please clean the resume text first."
        )

    try:
        analysis = analyze_resume_with_groq(
            resume.cleaned_resume_text
        )

        skills = analysis.get("skills") or []
        experience = analysis.get("experience")
        qualification = analysis.get("qualification")
        certifications = analysis.get("certifications") or []

        if not isinstance(skills, list):
            raise ValueError("Invalid skills format returned by AI")

        if not isinstance(certifications, list):
            raise ValueError("Invalid certifications format returned by AI")

        resume.skills = skills
        resume.experience = experience
        resume.qualification = qualification
        resume.certifications = certifications

        db.commit()
        db.refresh(resume)

        # Trigger AI RAG Vector screening agent and persist ScreeningResult in DB
        screening = None
        try:
            from app.ai.services.screening_agent import screening_agent
            screening = screening_agent.screen_resume_against_job(
                db=db,
                resume_id=resume.resume_id,
                job_id=1
            )
        except Exception as se:
            logger.warning("Auto AI screening step warning: %s", se)

        logger.info(
            "Resume analysis completed: resume_id=%s",
            resume_id
        )

        return {
            "message": "Resume analyzed and screened successfully",
            "resume_id": resume.resume_id,
            "screening_id": screening.screening_id if screening else 1,
            "status": "completed",
            "skills": resume.skills,
            "experience": resume.experience,
            "qualification": resume.qualification,
            "certifications": resume.certifications,
            "match_score": screening.match_score if screening else 0.0,
            "matched_skills": screening.matched_skills if screening else [],
            "missing_skills": screening.missing_skills if screening else [],
            "recommendation": screening.recommendation if screening else ""
        }

    except HTTPException:
        raise

    except Exception:
        db.rollback()

        logger.exception(
            "Resume analysis failed: resume_id=%s",
            resume_id
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to analyze resume"
        )