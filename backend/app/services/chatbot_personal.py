from sqlalchemy.orm import Session

from app.models.resume_tables import ScreeningResult


def get_user_latest_screening(
    db: Session,
    user_id: int
):
    result = (
        db.query(ScreeningResult)
        .filter(
            ScreeningResult.user_id == user_id
        )
        .order_by(
            ScreeningResult.created_at.desc()
        )
        .first()
    )

    if result is None:
        return None

    return {
        "screening_id": result.screening_id,
        "job_title": result.job.job_title if result.job else "Unknown",
        "match_score": result.match_score,
        "matched_skills": result.matched_skills or [],
        "missing_skills": result.missing_skills or [],
        "screening_result": result.screening_result,
        "recommendation": result.recommendation,
        "status": result.status,
        "progress": result.progress,
        "current_step": result.current_step
    }