from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.models.database import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class SoftDeleteMixin:
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class User(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    contact: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="candidate", nullable=False)

    resumes = relationship("Resume", back_populates="user")
    screening_results = relationship("ScreeningResult", back_populates="user")
    admin = relationship("Admin", back_populates="user", uselist=False)


class Resume(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "resumes"

    resume_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    resume_file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    resume_file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    resume_file_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    cleaned_resume_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    resume_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    skills: Mapped[list | None] = mapped_column(JSON, nullable=True)
    experience: Mapped[str | None] = mapped_column(String(100), nullable=True)
    qualification: Mapped[str | None] = mapped_column(String(255), nullable=True)
    certifications: Mapped[list | None] = mapped_column(JSON, nullable=True)

    user = relationship("User", back_populates="resumes")
    screening_results = relationship("ScreeningResult", back_populates="resume")

    @validates("resume_file_name", "resume_file_path", "resume_file_type", "cleaned_resume_text", "resume_text", "experience", "qualification")
    def sanitize_strings(self, key, value):
        if isinstance(value, str):
            return value.replace("\x00", "")
        return value


class Job(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "jobs"

    job_id: Mapped[int] = mapped_column(primary_key=True)
    job_title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    job_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    required_skills: Mapped[list | None] = mapped_column(JSON, nullable=True)
    required_experience: Mapped[str | None] = mapped_column(String(100), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)

    screening_results = relationship("ScreeningResult", back_populates="job")

    @validates("job_title", "job_description", "required_experience", "location", "category")
    def sanitize_strings(self, key, value):
        if isinstance(value, str):
            return value.replace("\x00", "")
        return value


class ScreeningResult(TimestampMixin, Base):
    __tablename__ = "screening_results"

    screening_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    resume_id: Mapped[int] = mapped_column(
        ForeignKey("resumes.resume_id", ondelete="CASCADE"), nullable=False, index=True
    )
    job_id: Mapped[int | None] = mapped_column(
        ForeignKey("jobs.job_id", ondelete="CASCADE"), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(
        String(50), default="PENDING", nullable=False, index=True
    )
    current_step: Mapped[str | None] = mapped_column(String(100), nullable=True)
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    matched_skills: Mapped[list | None] = mapped_column(JSON, nullable=True)
    missing_skills: Mapped[list | None] = mapped_column(JSON, nullable=True)
    match_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    screening_result: Mapped[str | None] = mapped_column(String(50), nullable=True)
    recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)

    user = relationship("User", back_populates="screening_results")
    resume = relationship("Resume", back_populates="screening_results")
    job = relationship("Job", back_populates="screening_results")

    @validates("status", "current_step", "screening_result", "recommendation")
    def sanitize_strings(self, key, value):
        if isinstance(value, str):
            return value.replace("\x00", "")
        return value



class Admin(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "admins"

    admin_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False
    )
    admin_name: Mapped[str] = mapped_column(String(100), nullable=False)
    admin_email: Mapped[str] = mapped_column(String(255), nullable=False)
    admin_contact: Mapped[str | None] = mapped_column(String(20), nullable=True)

    user = relationship("User", back_populates="admin")


class DailyScreeningStats(TimestampMixin, Base):
    __tablename__ = "daily_screening_stats"

    stat_id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    total_resumes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_screenings: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    selected_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    shortlisted_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rejected_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    job_profiles_summary: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    admin_id: Mapped[int | None] = mapped_column(
        ForeignKey("admins.admin_id", ondelete="SET NULL"), nullable=True
    )

    admin = relationship("Admin")