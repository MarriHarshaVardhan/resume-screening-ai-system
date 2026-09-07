import logging

from app.ai.services.embedding_service import generate_embedding
from app.ai.services.pinecone_service import get_pinecone_index
from app.dto.knowledge import (
    KnowledgeSearchDTO,
    KnowledgeSearchResponseDTO,
    KnowledgeSearchResultDTO,
)
from app.models.resume_tables import User
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

def search_knowledge(data: KnowledgeSearchDTO, current_user: User):
    query = data.query.strip()
    job_title = data.job_title.strip()

    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query cannot be empty"
        )

    if not job_title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job title cannot be empty"
        )

    try:
        embedding = generate_embedding(query)
        index = get_pinecone_index()

        response = index.query(
            vector=embedding,
            top_k=5,
            include_metadata=True,
            filter={
                "job_title": {
                    "$eq": job_title
                }
            }
        )

        results = []

        for match in response.get("matches", []):
            metadata = match.get("metadata", {})

            results.append(
                KnowledgeSearchResultDTO(
                    document_id=metadata.get("document_id", ""),
                    job_title=metadata.get("job_title", ""),
                    score=float(match.get("score", 0)),
                    text=metadata.get("text", "")
                )
            )

        logger.info(
            "Knowledge search completed: user_id=%s job_title=%s results=%s",
            current_user.user_id,
            job_title,
            len(results)
        )

        return KnowledgeSearchResponseDTO(
            query=query,
            results=results
        )

    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to search knowledge")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search knowledge"
        )