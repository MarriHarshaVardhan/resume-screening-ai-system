from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.models.database import get_db
from app.models.resume_tables import User

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
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # user_id = int(current_user["sub"]) if "sub" in current_user else None
    user_id= current_user.user_id
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return {
        "message": "User profile retrieved successfully",
        "data": {
            "user_id": user.user_id,
            "name": user.name,
            "contact": user.contact,
            "email": user.email,
            "role": user.role
        }
    }