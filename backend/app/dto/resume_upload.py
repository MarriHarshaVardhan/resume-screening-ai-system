from pydantic import BaseModel
from typing import List, Optional


class ResumeUploadResponseDTO(BaseModel):
    message: str
    resume_id: int
    file_name: str
    screening_id: Optional[int] = None
    match_score: Optional[float] = None
    status: Optional[str] = None
    recommendation: Optional[str] = None
    matched_skills: Optional[List[str]] = None
    missing_skills: Optional[List[str]] = None