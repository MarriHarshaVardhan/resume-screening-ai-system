import logging

from sqlalchemy.orm import Session

from app.models.resume_tables import Job
from app.dto.job import JobCreateRequest


logger = logging.getLogger(__name__)


def create_job(
    job_data: JobCreateRequest,
    db: Session
):
    logger.info(
        "Creating new job: %s",
        job_data.job_title
    )

    job = Job(
        job_title=job_data.job_title,
        job_description=job_data.job_description,
        required_skills=job_data.required_skills,
        required_experience=job_data.required_experience,
        location=job_data.location,
        category=job_data.category
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    logger.info(
        "Job created successfully: job_id=%s",
        job.job_id
    )

    return job


def get_all_jobs(db: Session):
    return (
        db.query(Job)
        .filter(Job.deleted_at.is_(None))
        .all()
    )


def get_job_by_id(
    job_id: int,
    db: Session
):
    return (
        db.query(Job)
        .filter(
            Job.job_id == job_id,
            Job.deleted_at.is_(None)
        )
        .first()
    )