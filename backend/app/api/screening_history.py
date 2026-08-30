from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.services.screening_history import get_screening_history

router = APIRouter(
    prefix="/screening-history",
    tags=["Screening History"]
)


@router.get("/")
def screening_history(
    db: Session = Depends(get_db)
):
    return get_screening_history(db)