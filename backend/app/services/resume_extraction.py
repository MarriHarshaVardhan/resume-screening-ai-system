import logging
from pathlib import Path

from app.ai.parsers.docx_parser import extract_text_from_docx
from app.ai.parsers.pdf_parser import extract_text_from_pdf
from app.models.resume_tables import Resume, User
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def extract_resume_text(
    resume_id: int,
    current_user: User,
    db: Session
):
    """
    Extract text from an uploaded resume and
    save the extracted text into the database.
    """

    logger.info(
        "Resume text extraction started: resume_id=%s, user_id=%s",
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
            "Resume not found: resume_id=%s, user_id=%s",
            resume_id,
            current_user.user_id
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    file_path = Path(
        resume.resume_file_path
    )

    if not file_path.exists():

        logger.error(
            "Resume file missing from storage: %s",
            file_path
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume file not found in storage"
        )

    file_extension = file_path.suffix.lower()

    logger.info(
        "Resume file type detected: %s",
        file_extension
    )

    try:

        if file_extension == ".pdf":

            extracted_text = extract_text_from_pdf(
                str(file_path)
            )

        elif file_extension == ".docx":

            extracted_text = extract_text_from_docx(
                str(file_path)
            )

        elif file_extension == ".doc":

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "DOC text extraction is not supported yet. "
                    "Please upload PDF or DOCX."
                )
            )

        else:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported resume file type"
            )

    except HTTPException:
        raise

    except Exception:

        logger.exception(
            "Resume text extraction failed: resume_id=%s",
            resume_id
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to extract text from resume"
        )

    if not extracted_text or not extracted_text.strip():

        logger.warning(
            "No text extracted from resume: resume_id=%s",
            resume_id
        )

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Unable to extract readable text from resume"
            )
        )

    try:

        resume.resume_text = extracted_text.strip()

        db.commit()

        db.refresh(resume)

        logger.info(
            "Resume text saved successfully: resume_id=%s",
            resume_id
        )

        return {
            "message": "Resume text extracted successfully",
            "resume_id": resume.resume_id,
            "status": "completed"
        }

    except Exception:

        db.rollback()

        logger.exception(
            "Failed to save extracted resume text: resume_id=%s",
            resume_id
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to save extracted resume text"
        )