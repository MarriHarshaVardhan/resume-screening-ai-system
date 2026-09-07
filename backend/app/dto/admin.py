from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AdminRegistrationRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str
    contact: str
    password: str = Field(..., min_length=5)


class AdminLoginRequest(BaseModel):
    email: str
    password: str


class AdminLoginResponse(BaseModel):
    message: str
    admin_id: int
    user_id: int
    admin_name: str
    admin_email: str
    access_token: str
    token_type: str


class AdminRegistrationResponse(BaseModel):
    message: str
    admin_id: int
    user_id: int
    admin_name: str
    admin_email: str
    access_token: str
    token_type: str


class AdminUserResponse(BaseModel):
    user_id: int
    name: str
    email: str
    contact: str
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminResumeResponse(BaseModel):
    resume_id: int
    user_id: int
    resume_file_name: str
    resume_file_type: str | None
    experience: str | None
    qualification: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminScreeningResponse(BaseModel):
    screening_id: int
    user_id: int
    resume_id: int
    job_id: int | None
    status: str
    progress: int
    match_score: float | None
    screening_result: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminDashboardResponse(BaseModel):
    total_users: int
    total_resumes: int
    total_screenings: int
    completed_screenings: int
    processing_screenings: int
    pending_screenings: int