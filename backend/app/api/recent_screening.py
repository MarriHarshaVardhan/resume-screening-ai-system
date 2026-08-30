from fastapi import APIRouter
from app.services.recent_screening import get_recent_screenings
from app.dto.recent_screening import RecentScreeningResponse


router = APIRouter(
    tags=["Screenings"]
)


@router.get("/screenings/recent", response_model=RecentScreeningResponse)
def recent_screenings():
    return get_recent_screenings()