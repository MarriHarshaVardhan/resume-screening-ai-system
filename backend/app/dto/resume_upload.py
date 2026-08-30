from pydantic import BaseModel


class ResumeUploadResponseDTO(BaseModel):
    message: str
    resume_id: int
    file_name: str