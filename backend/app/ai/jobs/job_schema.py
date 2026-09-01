from typing import List

from pydantic import BaseModel, Field


class JobSchema(BaseModel):

    job_title: str

    required_skills: List[str] = Field(
        default_factory=list
    )

    required_experience: str | None = None

    required_qualifications: List[str] = Field(
        default_factory=list
    )

    required_certifications: List[str] = Field(
        default_factory=list
    )