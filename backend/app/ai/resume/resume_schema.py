from typing import List

from pydantic import BaseModel, Field


class ResumeSchema(BaseModel):

    candidate_name: str | None = None

    email: str | None = None

    phone: str | None = None

    skills: List[str] = Field(
        default_factory=list
    )

    experience: List[str] = Field(
        default_factory=list
    )

    qualifications: List[str] = Field(
        default_factory=list
    )

    certifications: List[str] = Field(
        default_factory=list
    )

    projects: List[str] = Field(
        default_factory=list
    )