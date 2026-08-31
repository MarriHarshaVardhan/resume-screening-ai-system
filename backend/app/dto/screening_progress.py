from pydantic import BaseModel
from typing import List


class ScreeningStep(BaseModel):
    name: str
    status: str


class ScreeningProgressResponse(BaseModel):
    steps: List[ScreeningStep]
    progress_percentage: int
    status_message: str