import logging
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from app.models.resume_tables import User, Admin, Resume, Job, ScreeningResult, DailyScreeningStats
from app.core.security import hash_password
from app.dto.admin_dashboard import AdminCreateRequestDTO, AdminCreateResponseDTO, DailyStatsResponseDTO

logger = logging.getLogger(__name__)


def create_admin_account(db: Session, data: AdminCreateRequestDTO) -> AdminCreateResponseDTO:
    """
    Create an Admin user account and associated Admin record in DB.
    """
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address already registered"
        )

    hashed = hash_password(data.password)
    user = User(
        name=data.name,
        email=data.email,
        contact=data.contact,
        password_hash=hashed,
        role="admin"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    admin = Admin(
        user_id=user.user_id,
        admin_name=user.name,
        admin_email=user.email,
        admin_contact=user.contact
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)

    logger.info("Admin account created: admin_id=%s, user_id=%s", admin.admin_id, user.user_id)

    return AdminCreateResponseDTO(
        message="Admin account created successfully",
        admin_id=admin.admin_id,
        user_id=user.user_id,
        admin_name=admin.admin_name,
        admin_email=admin.admin_email
    )


def get_daily_screening_analytics(db: Session) -> DailyStatsResponseDTO:
    """
    Compute & return daily resume screening analytics:
    Total resumes today, job profile breakdown, selected, shortlisted, rejected count.
    """
    today_str = datetime.utcnow().strftime("%Y-%m-%d")

    # Calculate actual counts from DB tables
    start_of_day = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    resumes_today = db.query(Resume).filter(Resume.created_at >= start_of_day).count()
    screenings_today = db.query(ScreeningResult).filter(ScreeningResult.created_at >= start_of_day).all()

    selected = 0
    shortlisted = 0
    rejected = 0
    job_profiles: dict = {}

    for s in screenings_today:
        st = s.screening_result or s.status or ""
        if st.lower() == "selected":
            selected += 1
        elif st.lower() == "shortlisted":
            shortlisted += 1
        elif st.lower() in ["rejected", "not shortlisted"]:
            rejected += 1

        title = s.job.job_title if s.job else "General"
        job_profiles[title] = job_profiles.get(title, 0) + 1

    # Update or persist DailyScreeningStats record
    stats = db.query(DailyScreeningStats).filter(DailyScreeningStats.date == today_str).first()
    if not stats:
        stats = DailyScreeningStats(
            date=today_str,
            total_resumes=resumes_today,
            total_screenings=len(screenings_today),
            selected_count=selected,
            shortlisted_count=shortlisted,
            rejected_count=rejected,
            job_profiles_summary=job_profiles
        )
        db.add(stats)
    else:
        stats.total_resumes = resumes_today
        stats.total_screenings = len(screenings_today)
        stats.selected_count = selected
        stats.shortlisted_count = shortlisted
        stats.rejected_count = rejected
        stats.job_profiles_summary = job_profiles

    db.commit()

    return DailyStatsResponseDTO(
        date=today_str,
        total_resumes_today=resumes_today,
        total_screenings_today=len(screenings_today),
        selected_count=selected,
        shortlisted_count=shortlisted,
        rejected_count=rejected,
        job_profiles_summary=job_profiles
    )


def get_all_screenings_history(db: Session, limit: int = 50) -> dict:
    """
    Get comprehensive screening history across all resumes and job profiles for admin monitoring.
    """
    results = (
        db.query(ScreeningResult)
        .options(
            joinedload(ScreeningResult.user),
            joinedload(ScreeningResult.resume),
            joinedload(ScreeningResult.job)
        )
        .order_by(ScreeningResult.created_at.desc())
        .limit(limit)
        .all()
    )

    history_list = []
    for r in results:
        history_list.append({
            "screening_id": r.screening_id,
            "candidate_name": r.user.name if r.user else "Unknown",
            "candidate_email": r.user.email if r.user else "N/A",
            "job_title": r.job.job_title if r.job else "N/A",
            "match_score": r.match_score or 0.0,
            "status": r.screening_result or r.status or "Completed",
            "matched_skills": r.matched_skills or [],
            "missing_skills": r.missing_skills or [],
            "date": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else ""
        })

    return {
        "message": "Admin comprehensive screening history",
        "total_count": len(history_list),
        "screenings": history_list
    }
