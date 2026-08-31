from pydantic import BaseModel


class DashboardResponse(BaseModel):
    total_screenings: int
    completed: int
    in_progress: int
    average_match_score: int