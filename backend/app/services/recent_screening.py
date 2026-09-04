from sqlalchemy.orm import Session, joinedload

from app.dto.recent_screening import (
    RecentScreeningResponse,
    RecentScreening,
    RecentScreeningData,
)

from app.models.resume_tables import ScreeningResult, Resume


def get_recent_screenings(
    db: Session,
    user_id: int | None = None,
    limit: int = 10
) -> RecentScreeningResponse:

    query = db.query(ScreeningResult).options(
        joinedload(ScreeningResult.user),
        joinedload(ScreeningResult.resume).joinedload(Resume.user),
        joinedload(ScreeningResult.job)
    )

    # Show only the logged-in user's screenings
    if user_id is not None:
        query = query.filter(
            ScreeningResult.user_id == user_id
        )

    # Get actual screening records from database
    screenings = (
        query
        .order_by(ScreeningResult.created_at.desc())
        .limit(limit)
        .all()
    )

    recent_list = []

    for screening in screenings:

        # Candidate name
        candidate_name = "Unknown"

        if screening.user and screening.user.name:
            candidate_name = screening.user.name

        elif (
            screening.resume
            and screening.resume.user
            and screening.resume.user.name
        ):
            candidate_name = screening.resume.user.name

        # Job title
        job_title = (
            screening.job.job_title
            if screening.job and screening.job.job_title
            else "N/A"
        )

        # Match score
        match_score = (
            float(screening.match_score)
            if screening.match_score is not None
            else 0.0
        )

        # Status
        status = (
            screening.status
            or screening.screening_result
            or "Pending"
        )

        # Date
        date_str = (
            screening.created_at.strftime("%Y-%m-%d")
            if screening.created_at
            else ""
        )

        # Add actual database screening
        recent_list.append(
            RecentScreening(
                screening_id=screening.screening_id,
                candidate=candidate_name,
                job_title=job_title,
                match_score=match_score,
                status=status,
                date=date_str,
            )
        )

    return RecentScreeningResponse(
        message="Recent screening results",
        data=RecentScreeningData(
            recent_screenings=recent_list
        )
    )