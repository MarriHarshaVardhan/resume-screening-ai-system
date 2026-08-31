from typing import Optional

from pydantic import BaseModel, Field


class ScreeningResultResponse(BaseModel):

    screening_id: int

    candidate_name: Optional[str] = None

    job_title: Optional[str] = None

    match_score: Optional[float] = None

    matched_skills: list[str] = Field(default_factory=list)

    missing_skills: list[str] = Field(default_factory=list)

    experience: Optional[str] = None

    qualification: Optional[str] = None

    certifications: list[str] = Field(default_factory=list)

    recommendation: Optional[str] = None

    summary: Optional[str] = None