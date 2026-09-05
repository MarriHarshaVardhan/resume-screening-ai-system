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
    experience_assessment: Optional[str] = None
    qualification_assessment: Optional[str] = None
    strengths: list[str] = Field(default_factory=list)
    concerns: list[str] = Field(default_factory=list)
    score_breakdown: dict = Field(default_factory=dict)
    recommendation: Optional[str] = None
    summary: Optional[str] = None