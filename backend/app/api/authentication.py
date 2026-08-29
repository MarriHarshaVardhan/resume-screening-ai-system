from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.models.database import get_db

from app.dto.authentication import (
    RegistrationRequest,
    LoginRequest
)
from app.services.authentication import (
    register_user,
    login_user
)

router = APIRouter(
    prefix="/authentication",
    tags=["Authentication"]
)

@router.post("/registration")
def registration(
    request: RegistrationRequest,
    db: Session = Depends(get_db)
):
    return register_user(
        db=db,
        registration_data=request.data.registration
    )

@router.post("/login")
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    return login_user(
        db=db,
        login_data=request.data.login
    )

@router.get("/me")
def get_profile(
    current_user: dict = Depends(get_current_user)
):
    return {
        "message": "User profile retrieved successfully",
        "data": current_user
    }