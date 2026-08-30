from app.dto.screening_history import (
    ScreeningHistoryRequestDTO,
    ScreeningHistoryResponseDTO
)

from sqlalchemy.orm import Session


def get_screening_history(db: Session):
    
    return {
        "message": "screening history",
        "data": {
            "screening": {
                "job_title": "AI Full Stack Developer",
                "candidate": "John Doe",
                "match_score": 85.5,
                "status": "Selected",
                "date": "2026-08-29"
            }
        }
    }
