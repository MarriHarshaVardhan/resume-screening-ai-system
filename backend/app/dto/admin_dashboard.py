from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional


class AdminCreateRequestDTO(BaseModel):
    name: str = Field(..., min_length=2, description="Admin full name")
    email: str = Field(..., description="Admin email address")
    contact: str = Field(..., description="Admin contact number")
    password: str = Field(..., min_length=5, description="Admin password")


class AdminCreateResponseDTO(BaseModel):
    message: str
    admin_id: int
    user_id: int
    admin_name: str
    admin_email: str


class DailyStatsResponseDTO(BaseModel):
    date: str
    total_resumes_today: int
    total_screenings_today: int
    selected_count: int
    shortlisted_count: int
    rejected_count: int
    job_profiles_summary: Dict[str, int]


class JobDescriptionCreateDTO(BaseModel):
    job_title: str = Field(..., min_length=2, description="Title of the job profile")
    job_description: str = Field(..., min_length=10, description="Detailed job description text")
    required_skills: List[str] = Field(..., min_items=1, description="List of required skills")
    required_experience: str = Field("1+ years", description="Required professional experience")
    location: Optional[str] = Field(None, description="Job location")
    category: Optional[str] = Field(None, description="Job category / department")


class JobDescriptionResponseDTO(BaseModel):
    message: str
    job_id: int
    job_title: str
    job_description: Optional[str]
    required_skills: List[str]
    required_experience: Optional[str]
