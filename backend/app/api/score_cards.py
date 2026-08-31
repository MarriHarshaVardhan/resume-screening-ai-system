from fastapi import APIRouter
from app.dto.score_cards import DashboardResponse

router = APIRouter(prefix="/score-cards", tags=["Score Cards"])


@router.get("", response_model=DashboardResponse)
def get_dashboard():
    # Dummy data for now, will be replaced with real AI-based screening results later
    return DashboardResponse(
        total_screenings=24,
        completed=18,
        in_progress=3,
        average_match_score=78
    )