import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.ai.services.resume_analyzer import analyze_resume_with_groq
from app.models.resume_tables import (
    Resume,
    User,
    Job,
    ScreeningResult
)


logger = logging.getLogger(__name__)


def analyze_resume(
    resume_id: int,
    job_id: int,
    current_user: User,
    db: Session
):

    logger.info(
        "Resume analysis started: resume_id=%s, job_id=%s, user_id=%s",
        resume_id,
        job_id,
        current_user.user_id
    )

    # Get Resume

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

    # Get Job

    job = (
        db.query(Job)
        .filter(
            Job.job_id == job_id,
            Job.deleted_at.is_(None)
        )
        .first()
    )

    if not job:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    # Check Cleaned Resume Text

    if not resume.cleaned_resume_text:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Resume text is not cleaned. "
                "Please clean the resume text first."
            )
        )

    try:

        # AI Resume Analysis

        analysis = analyze_resume_with_groq(
            resume.cleaned_resume_text
        )

        skills = analysis.get("skills") or []
        experience = analysis.get("experience")
        qualification = analysis.get("qualification")
        certifications = analysis.get("certifications") or []

        if not isinstance(skills, list):

            raise ValueError(
                "Invalid skills format returned by AI"
            )

        if not isinstance(certifications, list):

            raise ValueError(
                "Invalid certifications format returned by AI"
            )

        # Save AI analysis into Resume

        resume.skills = skills
        resume.experience = experience
        resume.qualification = qualification
        resume.certifications = certifications

        db.commit()

        db.refresh(resume)

        # Compare Resume Skills
        # With Required Skills

        resume_skills_lower = {
            str(skill).strip().lower()
            for skill in skills
            if str(skill).strip()
        }

        required_skills = (
            job.required_skills or []
        )

        required_skills_lower = {
            str(skill).strip().lower()
            for skill in required_skills
            if str(skill).strip()
        }

        matched_skills = [
            skill
            for skill in required_skills
            if str(skill).strip().lower()
            in resume_skills_lower
        ]

        missing_skills = [
            skill
            for skill in required_skills
            if str(skill).strip().lower()
            not in resume_skills_lower
        ]

        # Calculate Match Score

        match_score = 0.0

        score_breakdown = []

        # Skills = 40 points

        if required_skills:

            skills_score = (
                len(matched_skills)
                / len(required_skills)
            ) * 40

            match_score += skills_score

            score_breakdown.append(
                f"Skills: {skills_score:.1f}/40"
            )

        # Experience = 30 points

        if experience and str(experience).strip():

            match_score += 30

            score_breakdown.append(
                "Experience: 30/30"
            )

        # Qualification = 20 points

        if qualification and str(qualification).strip():

            match_score += 20

            score_breakdown.append(
                "Qualification: 20/20"
            )

        # Certifications = 10 points

        if certifications:

            cert_score = min(
                len(certifications) * 3,
                10
            )

            match_score += cert_score

            score_breakdown.append(
                f"Certifications: {cert_score}/10"
            )

        # Maximum 100

        match_score = min(
            match_score,
            100.0
        )

        # Recommendation Status

        if match_score >= 75:

            recommendation_status = "Shortlisted"

        elif match_score >= 50:

            recommendation_status = "Under Review"

        elif match_score >= 30:

            recommendation_status = "On Hold"

        else:

            recommendation_status = "Rejected"

        # Recommendation

        recommendation = (
            f"Status: {recommendation_status} | "
            f"Score: {match_score:.1f}/100 | "
            f"Breakdown: {', '.join(score_breakdown)} | "
            f"Job: {job.job_title}"
        )

        # Create / Update Screening

        screening = (
            db.query(ScreeningResult)
            .filter(
                ScreeningResult.resume_id == resume_id,
                ScreeningResult.user_id == current_user.user_id,
                ScreeningResult.job_id == job_id
            )
            .first()
        )

        if not screening:

            screening = ScreeningResult(

                user_id=current_user.user_id,

                resume_id=resume_id,

                job_id=job_id,

                status="COMPLETED",

                current_step="Resume Analysis",

                progress=100,

                matched_skills=matched_skills,

                missing_skills=missing_skills,

                match_score=match_score,

                screening_result=recommendation_status,

                recommendation=recommendation
            )

            db.add(screening)

        else:

            screening.status = "COMPLETED"

            screening.current_step = (
                "Resume Analysis"
            )

            screening.progress = 100

            screening.matched_skills = (
                matched_skills
            )

            screening.missing_skills = (
                missing_skills
            )

            screening.match_score = (
                match_score
            )

            screening.screening_result = (
                recommendation_status
            )

            screening.recommendation = (
                recommendation
            )

        db.commit()

        db.refresh(screening)

        logger.info(
            "Resume analysis completed: "
            "resume_id=%s, job_id=%s, screening_id=%s",
            resume_id,
            job_id,
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

    except HTTPException as e:
        logger.error(
            f"HTTP Exception in resume analysis: {e.detail}"
        )
        raise

    except ValueError as e:
        db.rollback()
        logger.error(
            f"Value Error in resume analysis: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

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