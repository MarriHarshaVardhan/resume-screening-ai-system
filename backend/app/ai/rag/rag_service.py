from app.ai.embeddings.embedding_service import (
    embedding_service
)

from app.ai.vector_store.chroma_store import (
    chroma_store
)


def semantic_search(
    query: str,
    top_k: int = 5
):

    query_embedding = (
        embedding_service.create_embedding(
            query
        )
    )

    results = chroma_store.search(
        query_embedding,
        top_k
    )

    return results