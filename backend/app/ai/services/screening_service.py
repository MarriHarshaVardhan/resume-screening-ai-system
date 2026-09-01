from sqlalchemy.orm import Session

from app.ai.screening.screening_engine import (
    screen_resume
)


def create_screening(
    db: Session,
    user_id: int,
    resume_id: int,
    job_id: int,
    resume_text: str,
    job_requirements: str
):

    result = screen_resume(
        resume_text=resume_text,
        job_requirements=job_requirements
    )

    # Create your existing ScreeningResult model here.
    #
    # Example:
    #
    # screening = ScreeningResult(
    #     user_id=user_id,
    #     resume_id=resume_id,
    #     job_id=job_id,
    #     matched_skills=result.matched_skills,
    #     missing_skills=result.missing_skills,
    #     match_score=result.match_score,
    #     screening_result=result.explanation,
    #     recommendation=result.recommendation
    # )
    #
    # db.add(screening)
    # db.commit()
    # db.refresh(screening)

    return result