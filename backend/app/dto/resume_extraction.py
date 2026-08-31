from pydantic import BaseModel


class ResumeExtractionResponseDTO(BaseModel):

    message: str

    resume_id: int

    status: str