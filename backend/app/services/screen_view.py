from sqlalchemy.orm import Session

from app.models.resume_tables import ScreeningResult


def get_screening_result(
    db: Session,
    screening_id: int
):

    result = (
        db.query(ScreeningResult)
        .filter(
            ScreeningResult.screening_id == screening_id
        )
        .first()
    )

    if result is None:
        return None

    return {
        "screening_id": result.screening_id,

        "candidate_name": (
            result.user.name
            if result.user
            else "Unknown"
        ),

        "job_title": (
            result.job.job_title
            if result.job
            else "Unknown"
        ),

        "match_score": result.match_score,

        "matched_skills": result.matched_skills or [],

        "missing_skills": result.missing_skills or [],

        "experience": (
            result.resume.experience
            if result.resume
            else None
        ),

        "qualification": (
            result.resume.qualification
            if result.resume
            else None
        ),

        "certifications": (
            result.resume.certifications
            if result.resume
            and result.resume.certifications
            else []
        ),

        "screening_result": result.screening_result,

        "recommendation": result.recommendation,

        "status": result.status,

        "progress": result.progress,

        "current_step": result.current_step
    }