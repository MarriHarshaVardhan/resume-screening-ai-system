from typing import List, Dict, Any

from app.core.config import settings
from app.ai.vector_store.pinecone_store import pinecone_kb


def semantic_search(
    query: str,
    top_k: int | None = None
) -> List[Dict[str, Any]]:
    top_k = top_k or settings.RAG_TOP_K
    if pinecone_kb.index:
        try:
            from app.ai.embeddings.embedding_service import embedding_service
            vec = embedding_service.create_embedding(query) if query else [0.0] * pinecone_kb.dimension
            vec = pinecone_kb._pad_vector(vec)
            res = pinecone_kb.index.query(vector=vec, top_k=top_k, include_metadata=True)
            return res.to_dict() if hasattr(res, "to_dict") else res
        except Exception:
            pass
    return []