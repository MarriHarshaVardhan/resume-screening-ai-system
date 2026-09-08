from pydantic import BaseModel, Field


class ScreeningAgentRequestDTO(BaseModel):
    resume_id: int
    job_title: str = Field(min_length=1)

class ScreeningAgentResponseDTO(BaseModel):
    resume_id: int
    job_title: str
    matched_skills: list[str]
    missing_skills: list[str]
    match_score: float
    screening_result: str
    recommendation: str