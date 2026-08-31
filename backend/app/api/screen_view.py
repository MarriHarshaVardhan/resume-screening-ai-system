from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.services.screen_view import get_screening_result
from app.dto.screen_view import ScreeningResultResponse


router = APIRouter(
    prefix="/screening",
    tags=["Screening"]
)


@router.get(
    "/{screening_id}",
    response_model=ScreeningResultResponse
)
def view_screening_result(
    screening_id: int,
    db: Session = Depends(get_db)
):
    """
    Get complete screening result
    for the View Result screen.
    """

    result = get_screening_result(
        db=db,
        screening_id=screening_id
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Screening result not found"
        )

    return result