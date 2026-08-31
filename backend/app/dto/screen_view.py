from typing import Optional

from pydantic import BaseModel, Field


class ScreeningResultResponse(BaseModel):

    screening_id: int

    candidate_name: str

    job_title: str

    match_score: Optional[float] = None

    matched_skills: list[str] = Field(default_factory=list)

    missing_skills: list[str] = Field(default_factory=list)

    experience: Optional[str] = None

    qualification: Optional[str] = None

    certifications: list[str] = Field(default_factory=list)

    screening_result: Optional[str] = None

    recommendation: Optional[str] = None

    status: str

    progress: int

    current_step: Optional[str] = None