import logging
import uuid

from app.ai.services.embedding_service import generate_embedding
from app.ai.services.pinecone_service import upsert_knowledge
from app.ai.services.text_chunker import chunk_text
from app.dto.knowledge import KnowledgeAddDTO, KnowledgeAddResponseDTO
from app.models.resume_tables import User
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

def add_knowledge(data: KnowledgeAddDTO, current_user: User):
    text = data.jd_text.strip()

    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="JD text cannot be empty"
        )

    try:
        document_id = str(uuid.uuid4())
        chunks = chunk_text(text)

        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to create knowledge chunks"
            )

        vectors = []

        for index, chunk in enumerate(chunks):
            embedding = generate_embedding(chunk)
            vectors.append({
                "id": f"{document_id}-{index}",
                "values": embedding,
                "metadata": {
                    "document_id": document_id,
                    "job_title": data.job_title.strip(),
                    "document_type": "job_description",
                    "chunk_index": index,
                    "text": chunk
                }
            })

        upsert_knowledge(vectors)

        logger.info(
            "Knowledge added: document_id=%s job_title=%s chunks=%s user_id=%s",
            document_id,
            data.job_title,
            len(chunks),
            current_user.user_id
        )

        return KnowledgeAddResponseDTO(
            message="Knowledge added successfully",
            document_id=document_id,
            job_title=data.job_title.strip(),
            chunks_stored=len(chunks)
        )

    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to add knowledge")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add knowledge"
        )