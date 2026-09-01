from sentence_transformers import SentenceTransformer

from app.ai.config import ai_settings


class EmbeddingService:

    def __init__(self):

        self.model = SentenceTransformer(
            ai_settings.EMBEDDING_MODEL
        )

    def create_embedding(
        self,
        text: str
    ):

        if not text:
            raise ValueError(
                "Text cannot be empty"
            )

        embedding = self.model.encode(
            text,
            normalize_embeddings=True
        )

        return embedding.tolist()


embedding_service = EmbeddingService()