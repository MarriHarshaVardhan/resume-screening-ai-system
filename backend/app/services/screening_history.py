from datetime import datetime
from sqlalchemy.orm import Session, joinedload

from app.dto.screening_history import (
    ScreeningHistoryResponseDTO,
    ScreeningHistoryDataDTO,
    ScreeningDTO
)
from app.models.resume_tables import ScreeningResult, User, Job, Resume


def get_screening_history(db: Session, user_id: int | None = None) -> dict:
    target_user = None

    if user_id is not None:
        target_user = db.query(User).filter(User.user_id == user_id).first()

    query = db.query(ScreeningResult).options(
        joinedload(ScreeningResult.user),
        joinedload(ScreeningResult.resume).joinedload(Resume.user),
        joinedload(ScreeningResult.job)
    )

    if target_user:
        screening = query.filter(ScreeningResult.user_id == target_user.user_id).order_by(ScreeningResult.created_at.desc()).first()
    else:
        screening = query.order_by(ScreeningResult.created_at.desc()).first()
        if screening and screening.user:
            target_user = screening.user

    if screening:
        candidate_name = "Unknown"
        if screening.user and screening.user.name:
            candidate_name = screening.user.name
        elif screening.resume and screening.resume.user and screening.resume.user.name:
            candidate_name = screening.resume.user.name

        job_title = screening.job.job_title if (screening.job and screening.job.job_title) else "N/A"
        match_score = float(screening.match_score) if screening.match_score is not None else 0.0
        status = screening.screening_result or screening.status or "Completed"
        date_str = screening.created_at.strftime("%Y-%m-%d") if screening.created_at else ""

        return {
            "message": "screening history",
            "data": {
                "screening": {
                    "job_title": job_title,
                    "candidate": candidate_name,
                    "match_score": match_score,
                    "status": status,
                    "date": date_str
                }
            }
        }
    elif target_user:
        user_resume = db.query(Resume).filter(Resume.user_id == target_user.user_id).order_by(Resume.created_at.desc()).first()
        latest_job = db.query(Job).order_by(Job.created_at.desc()).first()

        job_title = latest_job.job_title if latest_job else "N/A"
        date_str = (
            user_resume.created_at.strftime("%Y-%m-%d") if (user_resume and user_resume.created_at)
            else (target_user.created_at.strftime("%Y-%m-%d") if target_user.created_at else "")
        )

        return {
            "message": "screening history",
            "data": {
                "screening": {
                    "job_title": job_title,
                    "candidate": target_user.name,
                    "match_score": 0.0,
                    "status": "Pending",
                    "date": date_str
                }
            }
        }
    else:
        return {
            "message": "screening history",
            "data": {
                "screening": {
                    "job_title": "N/A",
                    "candidate": "N/A",
                    "match_score": 0.0,
                    "status": "No screening found",
                    "date": ""
                }
            }
        }
