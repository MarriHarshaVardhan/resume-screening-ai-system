from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.resume_tables import User
from app.dto.authentication import RegistrationData, LoginData
from app.core.security import hash_password, verify_password, create_access_token


def register_user(
    db: Session,
    registration_data: RegistrationData
) -> dict:
    """
    Register a new user with the provided registration data.
    """
    # Check if user already exists by email
    existing_user = db.query(User).filter(
        User.email == registration_data.email
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Check if user already exists by contact
    existing_contact = db.query(User).filter(
        User.contact == registration_data.contact
    ).first()
    
    if existing_contact:
        raise HTTPException(
            status_code=400,
            detail="Contact number already registered"
        )
    
    # Hash the password
    hashed_password = hash_password(registration_data.password)
    
    # Create new user
    new_user = User(
        name=registration_data.name,
        email=registration_data.email,
        contact=registration_data.contact,
        password_hash=hashed_password,
        role="candidate"
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create access token
    access_token = create_access_token(
        user_id=new_user.user_id,
        email=new_user.email,
        role=new_user.role
    )
    
    return {
        "message": "User registered successfully",
        "user_id": new_user.user_id,
        "name": new_user.name,
        "contact": new_user.contact,
        "email": new_user.email,
        "access_token": access_token,
        "token_type": "bearer"
    }


def login_user(
    db: Session,
    login_data: LoginData
) -> dict:
    """
    Authenticate a user and return an access token.
    """
    # Find user by email or contact
    user = db.query(User).filter(
        (User.email == login_data.email_or_mobile) |
        (User.contact == login_data.email_or_mobile)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email/contact or password"
        )
    
    # Verify password
    if not verify_password(
        login_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email/contact or password"
        )
    
    # Create access token
    access_token = create_access_token(
        user_id=user.user_id,
        email=user.email,
        role=user.role
    )
    
    return {
        "message": "Login successful",
        "user_id": user.user_id,
        "name": user.name,
        "contact": user.contact,
        "email": user.email,
        "access_token": access_token,
        "token_type": "bearer"
    }
