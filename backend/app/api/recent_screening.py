from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.services.recent_screening import get_recent_screenings
from app.dto.recent_screening import RecentScreeningResponse
from app.core.security import get_current_user_optional


router = APIRouter(
    tags=["Screenings"]
)


@router.get("/screenings/recent", response_model=RecentScreeningResponse)
def recent_screenings(
    db: Session = Depends(get_db),
    current_user: dict | None = Depends(get_current_user_optional)
):
    user_id = int(current_user["sub"]) if (current_user and "sub" in current_user) else None
    return get_recent_screenings(db=db, user_id=user_id)