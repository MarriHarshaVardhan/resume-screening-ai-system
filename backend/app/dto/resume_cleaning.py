from pydantic import BaseModel


class ResumeCleaningResponseDTO(BaseModel):

    message: str

    resume_id: int

    status: str