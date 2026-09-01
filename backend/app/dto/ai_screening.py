from pydantic import BaseModel, Field
from typing import List, Optional


class AIScreeningRequestDTO(BaseModel):
    resume_id: int = Field(..., description="ID of the resume to screen")
    job_id: Optional[int] = Field(None, description="Optional target Job ID")


class AIScreeningResponseDTO(BaseModel):
    message: str
    screening_id: int
    candidate_name: str
    job_title: str
    match_score: float
    status: str
    matched_skills: List[str]
    missing_skills: List[str]
    recommendation: str


class KBSearchRequestDTO(BaseModel):
    query: str = Field(..., description="Search query or skill description")
    top_k: int = Field(5, description="Number of results to return")
