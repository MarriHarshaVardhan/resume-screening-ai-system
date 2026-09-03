import logging
import uuid

from pathlib import Path

from fastapi import (
    UploadFile,
    HTTPException,
    status
)

from sqlalchemy.orm import Session

from app.core.config import settings

from app.models.resume_tables import (
    Resume,
    User,
    Job
)


logger = logging.getLogger(__name__)


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx"
}


def upload_resume(
    file: UploadFile,
    job_title: str,
    required_skills: str,
    current_user: User,
    db: Session
):

    logger.info(
        "Resume upload started for user_id=%s",
        current_user.user_id
    )

    if not file:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume file is required"
        )

    if not file.filename:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume file name is required"
        )

    if not job_title or not job_title.strip():

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job title is required"
        )

    original_file_name = file.filename

    file_extension = Path(
        original_file_name
    ).suffix.lower()

    if file_extension not in ALLOWED_EXTENSIONS:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF, DOC and DOCX files are allowed"
        )

    try:

        file_content = file.file.read()

        file_size = len(file_content)

        if file_size == 0:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resume file is empty"
            )

        if file_size > settings.MAX_RESUME_FILE_SIZE:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resume file size must not exceed 10 MB"
            )

        upload_directory = Path(
            settings.UPLOAD_DIRECTORY
        )

        upload_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        unique_file_name = (
            f"{uuid.uuid4()}{file_extension}"
        )

        file_path = (
            upload_directory / unique_file_name
        )

        with open(
            file_path,
            "wb"
        ) as resume_file:

            resume_file.write(
                file_content
            )

        logger.info(
            "Resume file saved successfully: %s",
            file_path
        )

    except HTTPException:

        raise

    except Exception:

        logger.exception(
            "Resume file storage failed"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to save resume file"
        )

    try:

        # Convert comma-separated skills
        # Example:
        # Python, SQL, Flutter
        # →
        # ["Python", "SQL", "Flutter"]

        skills_list = [
            skill.strip()
            for skill in required_skills.split(",")
            if skill.strip()
        ]

        # Create Resume

        resume = Resume(
            user_id=current_user.user_id,
            resume_file_name=original_file_name,
            resume_file_path=str(file_path),
            resume_file_type=file_extension.replace(".", "")
        )

        db.add(resume)

        db.commit()

        db.refresh(resume)

        # Create Job

        job = Job(
            job_title=job_title.strip(),
            required_skills=skills_list
        )

        db.add(job)

        db.commit()

        db.refresh(job)

        logger.info(
            "Resume and Job created successfully: "
            "resume_id=%s, job_id=%s",
            resume.resume_id,
            job.job_id
        )

        return {
            "message": "Resume uploaded successfully",
            "resume_id": resume.resume_id,
            "job_id": job.job_id,
            "file_name": original_file_name
        }

    except Exception:

        db.rollback()

        logger.exception(
            "Resume or Job database creation failed"
        )

        if file_path.exists():

            file_path.unlink()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to save resume and job information"
        )

    finally:

        file.file.close()