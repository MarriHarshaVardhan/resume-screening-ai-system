from pydantic import BaseModel


class ScreeningDTO(BaseModel):
    job_title: str
    candidate: str
    match_score: float
    status: str
    date: str


class ScreeningHistoryDataDTO(BaseModel):
    screening: ScreeningDTO


class ScreeningHistoryRequestDTO(BaseModel):
    message: str
    data: ScreeningHistoryDataDTO


class ScreeningHistoryResponseDTO(BaseModel):
    message: str
    data: ScreeningHistoryDataDTO