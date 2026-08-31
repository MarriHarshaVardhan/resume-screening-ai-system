from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dto.screening_history import ScreeningHistoryResponseDTO
from app.models.database import get_db
from app.services.screening_history import get_screening_history
from app.core.security import get_current_user_optional

router = APIRouter(
    prefix="/screening-history",
    tags=["Screening History"]
)


@router.get("/", response_model=ScreeningHistoryResponseDTO)
def screening_history(
    db: Session = Depends(get_db),
    current_user: dict | None = Depends(get_current_user_optional)
):
    user_id = int(current_user["sub"]) if (current_user and "sub" in current_user) else None
    return get_screening_history(db=db, user_id=user_id)