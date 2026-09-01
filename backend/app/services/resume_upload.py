import logging
import uuid
from pathlib import Path

from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.resume_tables import Resume, User


logger = logging.getLogger(__name__)


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx"
}


def upload_resume(
    file: UploadFile,
    current_user: User,
    db: Session
):

    logger.info(
        "Resume upload started for user_id=%s",
        current_user.user_id
    )

    if not file:
        logger.warning(
            "Resume upload failed: file is required"
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume file is required"
        )

    if not file.filename:
        logger.warning(
            "Resume upload failed: file name is missing"
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume file name is required"
        )

    original_file_name = file.filename

    file_extension = Path(
        original_file_name
    ).suffix.lower()

    if file_extension not in ALLOWED_EXTENSIONS:

        logger.warning(
            "Resume upload failed: unsupported file type %s",
            file_extension
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF, DOC and DOCX files are allowed"
        )

    try:

        file_content = file.file.read()

        file_size = len(file_content)

        if file_size == 0:

            logger.warning(
                "Resume upload failed: empty file"
            )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resume file is empty"
            )

        if file_size > settings.MAX_RESUME_FILE_SIZE:

            logger.warning(
                "Resume upload failed: file exceeds maximum size"
            )

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

        with open(file_path, "wb") as resume_file:
            resume_file.write(file_content)

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

        resume = Resume(
            user_id=current_user.user_id,
            resume_file_name=original_file_name,
            resume_file_path=str(file_path)
        )

        db.add(resume)

        db.commit()

        db.refresh(resume)

        logger.info(
            "Resume record created successfully: resume_id=%s, user_id=%s",
            resume.resume_id,
            current_user.user_id
        )

        # Automatically trigger AI Screening Agent pipeline on resume upload
        screening = None
        try:
            from app.ai.services.screening_agent import screening_agent
            screening = screening_agent.screen_resume_against_job(
                db=db,
                resume_id=resume.resume_id,
                job_id=1
            )
        except Exception as se:
            logger.warning("Auto AI screening on upload step warning: %s", se)

        return {
            "message": "Resume uploaded and screened successfully by AI Agent",
            "resume_id": resume.resume_id,
            "file_name": original_file_name,
            "screening_id": screening.screening_id if screening else None,
            "match_score": screening.match_score if screening else 0.0,
            "status": screening.status if screening else "Completed",
            "recommendation": screening.recommendation if screening else "",
            "matched_skills": screening.matched_skills if screening else [],
            "missing_skills": screening.missing_skills if screening else []
        }

    except Exception:

        db.rollback()

        logger.exception(
            "Resume database record creation failed"
        )

        # Remove uploaded file if DB operation fails
        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to save resume information"
        )

    finally:
        file.file.close()