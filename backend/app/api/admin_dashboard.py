import logging
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.dto.admin_dashboard import AdminCreateRequestDTO, AdminCreateResponseDTO, DailyStatsResponseDTO
from app.services.admin_dashboard import (
    create_admin_account,
    get_daily_screening_analytics,
    get_all_screenings_history
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin Management & Screening Dashboard"]
)


@router.post("/create", response_model=AdminCreateResponseDTO)
def create_admin_api(
    payload: AdminCreateRequestDTO,
    db: Session = Depends(get_db)
):
    """
    Create an Admin account and Admin ID in the database.
    """
    return create_admin_account(db=db, data=payload)


@router.get("/daily-stats", response_model=DailyStatsResponseDTO)
def get_daily_stats_api(
    db: Session = Depends(get_db)
):
    """
    Retrieve daily resume screening metrics:
    - Total resumes uploaded today
    - Job profile breakdown
    - Selected, Shortlisted, and Rejected candidate counts
    """
    return get_daily_screening_analytics(db=db)


@router.get("/screening-history-all")
def get_all_screenings_api(
    limit: int = Query(50, description="Max screening records to retrieve"),
    db: Session = Depends(get_db)
):
    """
    Get complete screening history across all candidates and job profiles for Admin oversight.
    """
    return get_all_screenings_history(db=db, limit=limit)
