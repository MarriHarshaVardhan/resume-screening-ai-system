import logging

from docx import Document

logger = logging.getLogger(__name__)


def extract_text_from_docx(file_path: str) -> str:
    """
    Extract text from a DOCX resume.
    """

    logger.info(
        "DOCX text extraction started: %s",
        file_path
    )

    try:
        document = Document(file_path)

        extracted_paragraphs = []

        for paragraph in document.paragraphs:
            paragraph_text = paragraph.text.strip()

            if paragraph_text:
                extracted_paragraphs.append(
                    paragraph_text
                )

        extracted_text = "\n".join(
            extracted_paragraphs
        ).strip()

        logger.info(
            "DOCX text extraction completed successfully"
        )

        return extracted_text

    except Exception:
        logger.exception(
            "DOCX text extraction failed"
        )
        raise