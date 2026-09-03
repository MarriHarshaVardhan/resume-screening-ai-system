from pydantic import BaseModel


class ResumeAnalysisResponseDTO(BaseModel):

    message: str

    resume_id: int
    screening_id: int | None = None
    status: str

    skills: list[str]

    experience: str | None

    qualification: str | None
    certifications: list[str]
    match_score: float | None = None
    matched_skills: list[str] | None = None
    missing_skills: list[str] | None = None
    recommendation: str | None = None
