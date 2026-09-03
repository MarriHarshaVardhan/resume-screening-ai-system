import logging

from docx import Document


logger = logging.getLogger(__name__)


def extract_text_from_docx(file_path: str) -> str:
    """
    Extract text from a DOCX resume with fallback.
    """
    logger.info("DOCX text extraction started: %s", file_path)

    try:
        document = Document(file_path)
        extracted_paragraphs = []

        for paragraph in document.paragraphs:
            paragraph_text = paragraph.text.strip()
            if paragraph_text:
                extracted_paragraphs.append(paragraph_text.replace("\x00", ""))

        extracted_text = "\n".join(extracted_paragraphs).strip().replace("\x00", "")
        if extracted_text:
            logger.info("DOCX text extraction completed successfully")
            return extracted_text
    except Exception as e:
        logger.warning("DOCX parser fallback for %s: %s", file_path, e)

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            fallback_text = f.read(50000).strip().replace("\x00", "")
            if fallback_text:
                return fallback_text
    except Exception:
        pass

    return ""