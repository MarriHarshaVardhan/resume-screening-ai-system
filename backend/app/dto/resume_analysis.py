from pydantic import BaseModel


class ResumeAnalysisResponseDTO(BaseModel):
    message: str
    resume_id: int
    status: str
    skills: list[str]
    experience: str | None
    qualification: str | None
    certifications: list[str]