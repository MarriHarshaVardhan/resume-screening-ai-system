from typing import List

from pydantic import BaseModel, Field


class ScreeningResultSchema(BaseModel):

    matched_skills: List[str] = Field(
        default_factory=list
    )

    missing_skills: List[str] = Field(
        default_factory=list
    )

    experience_match: str | None = None

    qualification_match: str | None = None

    certification_match: str | None = None

    strengths: List[str] = Field(
        default_factory=list
    )

    weaknesses: List[str] = Field(
        default_factory=list
    )

    match_score: float = 0.0

    recommendation: str | None = None

    explanation: str | None = None