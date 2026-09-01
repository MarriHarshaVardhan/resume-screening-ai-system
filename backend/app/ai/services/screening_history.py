from sqlalchemy.orm import Session

from app.models.screening_result import ScreeningResult
from app.models.resume import Resume
from app.models.job import Job


def get_screening_history(
    db: Session,
    user_id: int
):

    results = (
        db.query(
            ScreeningResult,
            Resume,
            Job
        )
        .join(
            Resume,
            ScreeningResult.resume_id
            == Resume.resume_id
        )
        .join(
            Job,
            ScreeningResult.job_id
            == Job.job_id
        )
        .filter(
            ScreeningResult.user_id == user_id
        )
        .all()
    )

    screening_history = []

    for screening, resume, job in results:

        screening_history.append({

            "job_title": job.job_title,

            "candidate": (
                resume.candidate_name
                if hasattr(resume, "candidate_name")
                else None
            ),

            "match_score": screening.match_score,

            "status": screening.screening_result,

            "date": screening.created_at
        })

    return {
        "message": "screening history",

        "data": {
            "screening": screening_history
        }
    }