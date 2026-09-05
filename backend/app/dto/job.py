from pydantic import BaseModel


class JobCreateRequest(BaseModel):
    job_title: str
    job_description: str
    required_skills: list[str]
    required_experience: str | None = None
    location: str | None = None
    category: str | None = None


class JobResponse(BaseModel):
    job_id: int
    job_title: str
    job_description: str
    required_skills: list[str] | None
    required_experience: str | None
    location: str | None
    category: str | None

    class Config:
        from_attributes = True