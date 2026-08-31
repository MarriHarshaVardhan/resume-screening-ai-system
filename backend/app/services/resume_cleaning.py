import logging

from fastapi import HTTPException, status

from sqlalchemy.orm import Session

from app.models.resume_tables import Resume, User

from app.ai.preprocessors.text_cleaner import (
    clean_resume_text
)


logger = logging.getLogger(__name__)


def clean_resume_text_service(
    resume_id: int,
    current_user: User,
    db: Session
):
    """
    Clean extracted resume text and save the cleaned
    version separately in the database.
    """

    logger.info(
        "Resume text cleaning started: resume_id=%s, user_id=%s",
        resume_id,
        current_user.user_id
    )

    resume = (
        db.query(Resume)
        .filter(
            Resume.resume_id == resume_id,
            Resume.user_id == current_user.user_id,
            Resume.deleted_at.is_(None)
        )
        .first()
    )

    if not resume:

        logger.warning(
            "Resume not found for cleaning: resume_id=%s, user_id=%s",
            resume_id,
            current_user.user_id
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    if not resume.resume_text:

        logger.warning(
            "Resume text not available: resume_id=%s",
            resume_id
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Resume text is not available. "
                "Please extract resume text first."
            )
        )

    try:

        cleaned_text = clean_resume_text(
            resume.resume_text
        )

        if not cleaned_text:

            logger.warning(
                "Resume cleaning produced empty text: resume_id=%s",
                resume_id
            )

            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Unable to clean resume text"
            )

        resume.cleaned_resume_text = cleaned_text

        db.commit()

        db.refresh(resume)

        logger.info(
            "Resume text cleaned successfully: resume_id=%s",
            resume_id
        )

        return {
            "message": "Resume text cleaned successfully",
            "resume_id": resume.resume_id,
            "status": "completed"
        }

    except HTTPException:
        raise

    except Exception:

        db.rollback()

        logger.exception(
            "Resume text cleaning failed: resume_id=%s",
            resume_id
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to clean resume text"
        )