from app.ai.embeddings.embedding_service import (
    embedding_service
)

from app.ai.vector_store.chroma_store import (
    chroma_store
)


def index_resume(
    resume_id: int,
    resume_text: str,
    user_id: int
):

    embedding = (
        embedding_service.create_embedding(
            resume_text
        )
    )

    chroma_store.add_document(
        document_id=f"resume_{resume_id}",
        text=resume_text,
        embedding=embedding,
        metadata={
            "resume_id": str(resume_id),
            "user_id": str(user_id)
        }
    )

    return True