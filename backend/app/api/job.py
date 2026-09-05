import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.dto.job import JobCreateRequest, JobResponse
from app.models.database import get_db
from app.models.resume_tables import User
from app.services.job import create_job, get_all_jobs, get_job_by_id


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)


@router.post("/create", response_model=JobResponse)
def create_job_api(
    job_data: JobCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logger.info(
        "POST /jobs/create called by user_id=%s",
        current_user.user_id
    )

    return create_job(job_data=job_data, db=db)


@router.get("/list", response_model=list[JobResponse])
def list_jobs_api(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_all_jobs(db=db)


@router.get("/{job_id}", response_model=JobResponse)
def get_job_api(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    job = get_job_by_id(job_id=job_id, db=db)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    return job