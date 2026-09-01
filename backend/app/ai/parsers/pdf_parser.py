import logging

from pypdf import PdfReader


logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF resume with graceful raw text fallback.
    """
    logger.info("PDF text extraction started: %s", file_path)

    try:
        reader = PdfReader(file_path)
        extracted_pages = []

        for page_number, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text()
            if page_text:
                extracted_pages.append(page_text)
            logger.debug("Processed PDF page %s", page_number)

        extracted_text = "\n".join(extracted_pages).strip()
        if extracted_text:
            logger.info("PDF text extraction completed successfully")
            return extracted_text
    except Exception as e:
        logger.warning("PDF stream reader fallback triggered for %s: %s", file_path, e)

    # Raw text fallback for plain text or stream formatted files
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            fallback_text = f.read().strip()
            if fallback_text:
                return fallback_text
    except Exception:
        pass

    return ""