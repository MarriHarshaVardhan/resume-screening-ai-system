import logging

from app.core.config import settings
from pinecone import Pinecone, ServerlessSpec

logger = logging.getLogger(__name__)

pc = Pinecone(api_key=settings.PINECONE_API_KEY)

def create_pinecone_index():
    index_name = settings.PINECONE_INDEX_NAME
    existing_indexes = pc.list_indexes().names()

    if index_name not in existing_indexes:
        pc.create_index(
            name=index_name,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        logger.info("Pinecone index created: %s", index_name)
    else:
        logger.info("Pinecone index already exists: %s", index_name)

def get_pinecone_index():
    try:
        return pc.Index(settings.PINECONE_INDEX_NAME)
    except Exception:
        logger.exception("Failed to connect to Pinecone")
        raise

def upsert_knowledge(vectors: list[dict]):
    index = get_pinecone_index()
    index.upsert(vectors=vectors)
    logger.info("Stored %s vectors in Pinecone", len(vectors))

def delete_knowledge(document_id: str):
    index = get_pinecone_index()
    index.delete(filter={"document_id": document_id})
    logger.info("Knowledge deleted: document_id=%s", document_id)