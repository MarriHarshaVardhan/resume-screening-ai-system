import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.ai.services.resume_analyzer import analyze_resume_with_groq
from app.models.resume_tables import Resume, User, ScreeningResult


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

        # Create or update screening result
        screening = db.query(ScreeningResult).filter(
            ScreeningResult.resume_id == resume_id,
            ScreeningResult.user_id == current_user.user_id,
            ScreeningResult.job_id.is_(None)
        ).first()

        # Calculate match score based on resume analysis
        match_score = 0.0
        score_breakdown = []
        
        # Skills score (40 points max)
        if skills and len(skills) > 0:
            skills_score = min(len(skills) * 5, 40)
            match_score += skills_score
            score_breakdown.append(f"Skills: {skills_score}/40")
        
        # Experience score (30 points max)
        if experience and experience.strip():
            match_score += 30
            score_breakdown.append(f"Experience: 30/30")
        
        # Qualification score (20 points max)
        if qualification and qualification.strip():
            match_score += 20
            score_breakdown.append(f"Qualification: 20/20")
        
        # Certifications score (10 points max)
        if certifications and len(certifications) > 0:
            cert_score = min(len(certifications) * 3, 10)
            match_score += cert_score
            score_breakdown.append(f"Certifications: {cert_score}/10")
        
        # Ensure score doesn't exceed 100
        match_score = min(match_score, 100.0)
        
        # Determine recommendation status based on score
        if match_score >= 75:
            recommendation_status = "Shortlisted"
        elif match_score >= 50:
            recommendation_status = "Under Review"
        elif match_score >= 30:
            recommendation_status = "On Hold"
        else:
            recommendation_status = "Rejected"
        
        # Prepare recommendation with status
        recommendation = f"Status: {recommendation_status} | Score: {match_score:.1f}/100 | Breakdown: {', '.join(score_breakdown) if score_breakdown else 'No data'} | Analyzed: {resume.updated_at.strftime('%Y-%m-%d')}"

        if not screening:
            screening = ScreeningResult(
                user_id=current_user.user_id,
                resume_id=resume_id,
                job_id=None,
                status="COMPLETED",
                current_step="Resume Analysis",
                progress=100,
                matched_skills=skills,
                missing_skills=certifications,
                match_score=match_score,
                screening_result=recommendation_status,
                recommendation=recommendation
            )
            db.add(screening)
        else:
            screening.status = "COMPLETED"
            screening.current_step = "Resume Analysis"
            screening.progress = 100
            screening.matched_skills = skills
            screening.missing_skills = certifications
            screening.match_score = match_score
            screening.screening_result = recommendation_status
            screening.recommendation = recommendation

        db.commit()
        db.refresh(screening)

        logger.info(
            "Resume analysis completed: resume_id=%s, screening_id=%s",
            resume_id,
            screening.screening_id
        )

        return {
            "message": "Resume analyzed successfully",
            "resume_id": resume.resume_id,
            "screening_id": screening.screening_id,
            "status": "completed",
            "skills": resume.skills,
            "experience": resume.experience,
            "qualification": resume.qualification,
            "certifications": resume.certifications
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