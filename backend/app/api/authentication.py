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

@router.post(
    "/registration",
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "example": {
                        "data": {
                            "registration": {
                                "name": "John Doe",
                                "email": "john@example.com",
                                "contact": "9876543210",
                                "password": "Password@123"
                            }
                        },
                        "message": "Registration"
                    }
                }
            }
        }
    }
)
def registration(
    request: RegistrationRequest,
    db: Session = Depends(get_db)
):
    return register_user(
        db=db,
        registration_data=request.data.registration
    )

@router.post(
    "/login",
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "example": {
                        "data": {
                            "login": {
                                "email_or_mobile": "john@example.com",
                                "password": "Password@123"
                            }
                        },
                        "message": "Login"
                    }
                }
            }
        }
    }
)
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
    user_id = int(current_user["sub"]) if isinstance(current_user, dict) and "sub" in current_user else getattr(current_user, "user_id", None)
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