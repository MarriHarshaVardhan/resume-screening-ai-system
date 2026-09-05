import logging
import uuid
from pathlib import Path

from app.ai.parsers.docx_parser import extract_text_from_docx
from app.ai.parsers.pdf_parser import extract_text_from_pdf
from app.ai.services.embedding_service import generate_embedding
from app.ai.services.pinecone_service import upsert_knowledge
from app.ai.services.text_chunker import chunk_text
from app.core.config import settings
from app.dto.knowledge import KnowledgeUploadResponseDTO
from app.models.resume_tables import User
from fastapi import HTTPException, UploadFile, status

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}

def upload_knowledge(file: UploadFile, job_title: str, current_user: User):
    file_extension = Path(file.filename or "").suffix.lower()

    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF, DOCX and TXT files are supported"
        )

    try:
        file_content = file.file.read()

        if not file_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty"
            )

        knowledge_directory = Path("uploads/knowledge")
        knowledge_directory.mkdir(parents=True, exist_ok=True)

        document_id = str(uuid.uuid4())
        file_path = knowledge_directory / f"{document_id}{file_extension}"
        file_path.write_bytes(file_content)

        if file_extension == ".pdf":
            text = extract_text_from_pdf(str(file_path))
        elif file_extension == ".docx":
            text = extract_text_from_docx(str(file_path))
        else:
            text = file_content.decode("utf-8")

        text = text.strip()

        if not text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No text could be extracted from the document"
            )

        chunks = chunk_text(text)

        vectors = []

        for index, chunk in enumerate(chunks):
            embedding = generate_embedding(chunk)

            vectors.append({
                "id": f"{document_id}-{index}",
                "values": embedding,
                "metadata": {
                    "document_id": document_id,
                    "job_title": job_title,
                    "document_type": "job_description",
                    "chunk_index": index,
                    "text": chunk
                }
            })

        upsert_knowledge(vectors)

        logger.info(
            "Knowledge document uploaded: document_id=%s job_title=%s chunks=%s user_id=%s",
            document_id,
            job_title,
            len(chunks),
            current_user.user_id
        )

        return KnowledgeUploadResponseDTO(
            message="Knowledge document uploaded successfully",
            document_id=document_id,
            job_title=job_title,
            chunks_stored=len(chunks)
        )

    except HTTPException:
        raise
    except Exception:
        logger.exception("Knowledge document upload failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process knowledge document"
        )