from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_admin
from app.models.database import get_db
from app.models.resume_tables import User

from app.dto.admin import (
    AdminRegistrationRequest,
    AdminRegistrationResponse,
    AdminLoginRequest,
    AdminLoginResponse,
    AdminDashboardResponse,
    AdminResumeResponse,
    AdminScreeningResponse,
    AdminUserResponse,
)

from app.services.admin import (
    register_admin,
    login_admin,
    get_dashboard_stats,
    get_all_users,
    get_all_resumes,
    get_all_screenings,
    get_screening_by_id,
)

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


# Admin Registration

@router.post(
    "/registration",
    response_model=AdminRegistrationResponse,
)
def admin_registration(
    request: AdminRegistrationRequest,
    db: Session = Depends(get_db),
):
    return register_admin(
        db=db,
        registration_data=request,
    )


# Admin Login

@router.post(
    "/login",
    response_model=AdminLoginResponse,
)
def admin_login(
    request: AdminLoginRequest,
    db: Session = Depends(get_db),
):
    return login_admin(
        db=db,
        login_data=request,
    )


# Admin Dashboard

@router.get(
    "/dashboard",
    response_model=AdminDashboardResponse,
)
def admin_dashboard(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return get_dashboard_stats(db)


# Get All Users

@router.get(
    "/users",
    response_model=list[AdminUserResponse],
)
def get_users(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return get_all_users(db)


# Get All Resumes

@router.get(
    "/resumes",
    response_model=list[AdminResumeResponse],
)
def get_resumes(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return get_all_resumes(db)


# Get All Screenings

@router.get(
    "/screenings",
    response_model=list[AdminScreeningResponse],
)
def get_screenings(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return get_all_screenings(db)


# Get Screening Detail

@router.get(
    "/screenings/{screening_id}",
    response_model=AdminScreeningResponse,
)
def get_screening(
    screening_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    screening = get_screening_by_id(
        db=db,
        screening_id=screening_id,
    )

    if not screening:
        raise HTTPException(
            status_code=404,
            detail="Screening not found",
        )

    return screening