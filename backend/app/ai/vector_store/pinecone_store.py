import logging
from typing import List, Tuple
from app.core.config import settings
from app.ai.rag.kb_vector_engine import kb_engine

logger = logging.getLogger(__name__)


class PineconeVectorKB:
    """
    Pinecone Vector Database & Knowledge Base Engine.
    Handles vector indexing, metadata storage, and RAG similarity searches.
    Falls back gracefully to local vector engine if Pinecone API key is unconfigured.
    """

    def __init__(self):
        self.api_key = settings.PINECONE_API_KEY
        self.index_name = settings.PINECONE_INDEX_NAME
        self.dimension = settings.PINECONE_VECTOR_DIMENSION
        self.client = None
        self.index = None

        if self.api_key and not self.api_key.startswith("your-"):
            try:
                from pinecone import Pinecone, ServerlessSpec
                self.client = Pinecone(api_key=self.api_key)
                existing_indexes = [idx.name for idx in self.client.list_indexes()]
                if self.index_name not in existing_indexes:
                    self.client.create_index(
                        name=self.index_name,
                        dimension=self.dimension,
                        metric=settings.PINECONE_METRIC,
                        spec=ServerlessSpec(
                            cloud=settings.PINECONE_CLOUD,
                            region=settings.PINECONE_REGION
                        )
                    )
                self.index = self.client.Index(self.index_name)
                logger.info(
                    "Pinecone Vector DB initialized on index '%s' (dim=%s)",
                    self.index_name,
                    self.dimension
                )
            except Exception as e:
                logger.warning("Pinecone DB initialization fallback: %s", e)

    def _pad_vector(self, vec: list) -> list:
        """Pad or truncate vector to match configured dimension."""
        if len(vec) < self.dimension:
            vec = vec + [0.0] * (self.dimension - len(vec))
        elif len(vec) > self.dimension:
            vec = vec[:self.dimension]
        return vec

    def upsert_resume_vector(self, resume_id: int, text: str, metadata: dict):
        """
        Embed resume text into vector format and upsert into Pinecone Vector DB.
        """
        if self.index and text and text.strip():
            try:
                from app.ai.embeddings.embedding_service import embedding_service
                vec = embedding_service.create_embedding(text)
                vec = self._pad_vector(vec)

                # Pinecone requires at least one non-zero component
                if not any(vec):
                    vec[0] = 1e-6

                self.index.upsert(
                    vectors=[
                        {
                            "id": f"resume_{resume_id}",
                            "values": vec,
                            "metadata": metadata or {}
                        }
                    ]
                )
                logger.info("Upserted resume vector %s to Pinecone DB", resume_id)
            except Exception as e:
                logger.warning("Pinecone upsert fallback: %s", e)



    def query_kb_vectors(
        self,
        resume_skills: List[str],
        required_skills: List[str],
        resume_text: str,
        job_description: str
    ) -> Tuple[List[str], List[str], float]:
        """
        Perform RAG Vector similarity matching between Candidate Resume and Job Description.
        """
        return kb_engine.rag_skill_match(
            resume_skills=resume_skills,
            required_skills=required_skills,
            resume_text=resume_text,
            job_description=job_description
        )


pinecone_kb = PineconeVectorKB()

