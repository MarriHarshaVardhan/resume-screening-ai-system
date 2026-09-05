import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.resume_tables import Resume, User

from app.ai.preprocessors.text_cleaner import (
    clean_resume_text
)

from app.ai.embeddings.chroma_service import (
    add_resume
)


logger = logging.getLogger(__name__)


def clean_resume_text_service(
    resume_id: int,
    current_user: User,
    db: Session
):
    """
    Clean extracted resume text,
    save the cleaned text into PostgreSQL,
    and store its embedding in ChromaDB.
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

        # Clean the extracted resume text
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

        # Save cleaned text in PostgreSQL
        resume.cleaned_resume_text = cleaned_text

        db.commit()

        db.refresh(resume)

        logger.info(
            "Resume text cleaned and saved successfully: resume_id=%s",
            resume_id
        )

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

    try:

        # Store cleaned resume in ChromaDB
        add_resume(
            resume_id=str(resume.resume_id),
            resume_text=cleaned_text
        )

        logger.info(
            "Resume embedding stored in ChromaDB: resume_id=%s",
            resume_id
        )

    except Exception:

        logger.exception(
            "Failed to store resume embedding in ChromaDB: resume_id=%s",
            resume_id
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to store resume in vector database"
        )

    return {
        "message": "Resume text cleaned and stored successfully",
        "resume_id": resume.resume_id,
        "status": "completed"
    }