from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from app.dto.recent_screening import RecentScreeningResponse, RecentScreening, RecentScreeningData
from app.models.resume_tables import ScreeningResult, User, Job, Resume


def get_recent_screenings(db: Session, user_id: int | None = None, limit: int = 10) -> RecentScreeningResponse:

    target_user = None
    if user_id is not None:
        target_user = db.query(User).filter(User.user_id == user_id).first()

    query = db.query(ScreeningResult).options(
        joinedload(ScreeningResult.user),
        joinedload(ScreeningResult.resume).joinedload(Resume.user),
        joinedload(ScreeningResult.job)
    )

    if target_user:
        screenings = query.filter(ScreeningResult.user_id == target_user.user_id).order_by(ScreeningResult.created_at.desc()).limit(limit).all()
    else:
        screenings = query.order_by(ScreeningResult.created_at.desc()).limit(limit).all()

    recent_list = []
    if screenings:
        for s in screenings:
            candidate_name = "Unknown"
            if s.user and s.user.name:
                candidate_name = s.user.name
            elif s.resume and s.resume.user and s.resume.user.name:
                candidate_name = s.resume.user.name

            job_title = s.job.job_title if (s.job and s.job.job_title) else "N/A"
            match_score = float(s.match_score) if s.match_score is not None else 0.0
            status = s.screening_result or s.status or "Completed"
            date_str = s.created_at.strftime("%Y-%m-%d") if s.created_at else ""

            recent_list.append(
                RecentScreening(
                    screening_id=s.screening_id,
                    candidate=candidate_name,
                    job_title=job_title,
                    match_score=match_score,
                    status=status,
                    date=date_str
                )
            )
    elif target_user:
        user_resume = db.query(Resume).filter(Resume.user_id == target_user.user_id).order_by(Resume.created_at.desc()).first()
        latest_job = db.query(Job).order_by(Job.created_at.desc()).first()

        job_title = latest_job.job_title if latest_job else "N/A"
        date_str = (
            user_resume.created_at.strftime("%Y-%m-%d") if (user_resume and user_resume.created_at)
            else (target_user.created_at.strftime("%Y-%m-%d") if target_user.created_at else "")
        )

        recent_list.append(
            RecentScreening(
                screening_id=user_resume.resume_id if user_resume else 1,
                candidate=target_user.name,
                job_title=job_title,
                match_score=0.0,
                status="Pending",
                date=date_str
            )
        )

    return RecentScreeningResponse(
        message="Recent screening results",
        data=RecentScreeningData(
            recent_screenings=recent_list
        )
    )