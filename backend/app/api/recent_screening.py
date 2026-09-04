from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.services.recent_screening import get_recent_screenings
from app.dto.recent_screening import RecentScreeningResponse
from app.core.security import get_current_user_optional
from app.models.resume_tables import ScreeningResult


router = APIRouter(tags=["Screenings"])


@router.get(
    "/screenings/recent",
    response_model=RecentScreeningResponse
)
def recent_screenings(
    db: Session = Depends(get_db),
    current_user: dict | None = Depends(get_current_user_optional)
):
    user_id = int(current_user["sub"]) if (
        current_user and "sub" in current_user
    ) else None

    return get_recent_screenings(
        db=db,
        user_id=user_id
    )


@router.get("/screenings", response_model=RecentScreeningResponse)
def all_screenings(
    db: Session = Depends(get_db),
    current_user: dict | None = Depends(get_current_user_optional)
):
    user_id = int(current_user["sub"]) if (
        current_user and "sub" in current_user
    ) else None

    return get_recent_screenings(
        db=db,
        user_id=user_id,
        limit=1000
    )


@router.get("/dashboard/stats")
def dashboard_stats(
    db: Session = Depends(get_db),
    current_user: dict | None = Depends(get_current_user_optional),
):
    user_id = int(current_user["sub"]) if (
        current_user and "sub" in current_user
    ) else None

    query = db.query(ScreeningResult)

    if user_id is not None:
        query = query.filter(
            ScreeningResult.user_id == user_id
        )

    screenings = query.all()

    total_screenings = len(screenings)

    completed = sum(
        1
        for screening in screenings
        if str(screening.status).upper() == "COMPLETED"
    )

    in_progress = sum(
        1
        for screening in screenings
        if str(screening.status).upper()
        in ["PENDING", "PROCESSING", "IN_PROGRESS"]
    )

    scores = [
        float(screening.match_score)
        for screening in screenings
        if screening.match_score is not None
    ]

    average_match_score = (
        sum(scores) / len(scores)
        if scores
        else 0
    )

    return {
        "total_screenings": total_screenings,
        "completed": completed,
        "in_progress": in_progress,
        "average_match_score": average_match_score,
    }