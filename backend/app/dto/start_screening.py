from pydantic import BaseModel, Field

class StartScreeningDTO(BaseModel):
    resume_id: int
    job_title: str = Field(min_length=1)
    required_skills: list[str] = Field(min_length=1)

class StartScreeningResponseDTO(BaseModel):
    screening_id: int
    resume_id: int
    job_id: int
    status: str
    current_step: str
    progress: int
    matched_skills: list[str]
    missing_skills: list[str]
    match_score: float
    screening_result: str
    recommendation: str