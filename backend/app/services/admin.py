from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)

from app.models.resume_tables import (
    User,
    Admin,
    Resume,
    ScreeningResult,
)

from app.dto.admin import (
    AdminRegistrationRequest,
    AdminLoginRequest,
)


def register_admin(
    db: Session,
    registration_data: AdminRegistrationRequest,
) -> dict:

    # Check email
    existing_user = (
        db.query(User)
        .filter(User.email == registration_data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    # Check contact
    existing_contact = (
        db.query(User)
        .filter(User.contact == registration_data.contact)
        .first()
    )

    if existing_contact:
        raise HTTPException(
            status_code=400,
            detail="Contact number already registered",
        )

    # Hash password
    hashed_password = hash_password(
        registration_data.password
    )

    # Create user with admin role
    new_user = User(
        name=registration_data.name,
        email=registration_data.email,
        contact=registration_data.contact,
        password_hash=hashed_password,
        role="admin",
    )

    db.add(new_user)
    db.flush()

    # Create admin profile
    new_admin = Admin(
        user_id=new_user.user_id,
        admin_name=new_user.name,
        admin_email=new_user.email,
        admin_contact=new_user.contact,
    )

    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    db.refresh(new_user)

    # Create JWT token
    access_token = create_access_token(
        user_id=new_user.user_id,
        email=new_user.email,
        role=new_user.role,
    )

    return {
        "message": "Admin registered successfully",
        "admin_id": new_admin.admin_id,
        "user_id": new_user.user_id,
        "admin_name": new_admin.admin_name,
        "admin_email": new_admin.admin_email,
        "access_token": access_token,
        "token_type": "bearer",
    }


def login_admin(
    db: Session,
    login_data: AdminLoginRequest,
) -> dict:

    # Find user by email
    user = (
        db.query(User)
        .filter(
            User.email == login_data.email,
            User.deleted_at.is_(None),
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    # Check admin role
    if user.role.lower() != "admin":
        raise HTTPException(
            status_code=403,
            detail="User is not an admin",
        )

    # Verify password
    if not verify_password(
        login_data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    # Find admin profile
    admin = (
        db.query(Admin)
        .filter(
            Admin.user_id == user.user_id,
            Admin.deleted_at.is_(None),
        )
        .first()
    )

    if not admin:
        raise HTTPException(
            status_code=404,
            detail="Admin profile not found",
        )

    # Create JWT
    access_token = create_access_token(
        user_id=user.user_id,
        email=user.email,
        role=user.role,
    )

    return {
        "message": "Admin login successful",
        "admin_id": admin.admin_id,
        "user_id": user.user_id,
        "admin_name": admin.admin_name,
        "admin_email": admin.admin_email,
        "access_token": access_token,
        "token_type": "bearer",
    }


def get_admin_by_user_id(
    db: Session,
    user_id: int,
):
    return (
        db.query(Admin)
        .filter(
            Admin.user_id == user_id,
            Admin.deleted_at.is_(None),
        )
        .first()
    )


def get_dashboard_stats(db: Session):

    total_users = (
        db.query(func.count(User.user_id))
        .filter(User.deleted_at.is_(None))
        .scalar()
    )

    total_resumes = (
        db.query(func.count(Resume.resume_id))
        .filter(Resume.deleted_at.is_(None))
        .scalar()
    )

    total_screenings = (
        db.query(
            func.count(ScreeningResult.screening_id)
        )
        .scalar()
    )

    completed_screenings = (
        db.query(
            func.count(ScreeningResult.screening_id)
        )
        .filter(
            ScreeningResult.status == "COMPLETED"
        )
        .scalar()
    )

    processing_screenings = (
        db.query(
            func.count(ScreeningResult.screening_id)
        )
        .filter(
            ScreeningResult.status == "PROCESSING"
        )
        .scalar()
    )

    pending_screenings = (
        db.query(
            func.count(ScreeningResult.screening_id)
        )
        .filter(
            ScreeningResult.status == "PENDING"
        )
        .scalar()
    )

    return {
        "total_users": total_users or 0,
        "total_resumes": total_resumes or 0,
        "total_screenings": total_screenings or 0,
        "completed_screenings": completed_screenings or 0,
        "processing_screenings": processing_screenings or 0,
        "pending_screenings": pending_screenings or 0,
    }


def get_all_users(db: Session):

    return (
        db.query(User)
        .filter(User.deleted_at.is_(None))
        .order_by(User.created_at.desc())
        .all()
    )


def get_all_resumes(db: Session):

    return (
        db.query(Resume)
        .filter(Resume.deleted_at.is_(None))
        .order_by(Resume.created_at.desc())
        .all()
    )


def get_all_screenings(db: Session):

    return (
        db.query(ScreeningResult)
        .order_by(ScreeningResult.created_at.desc())
        .all()
    )


def get_screening_by_id(
    db: Session,
    screening_id: int,
):

    return (
        db.query(ScreeningResult)
        .filter(
            ScreeningResult.screening_id == screening_id
        )
        .first()
    )