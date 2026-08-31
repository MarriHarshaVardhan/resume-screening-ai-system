from pydantic import BaseModel
from typing import List


class RecentScreening(BaseModel):
    screening_id: int
    candidate: str
    job_title: str
    match_score: float
    status: str
    date: str


class RecentScreeningData(BaseModel):
    recent_screenings: List[RecentScreening]


class RecentScreeningResponse(BaseModel):
    message: str
    data: RecentScreeningData