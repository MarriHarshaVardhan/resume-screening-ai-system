from app.ai.config import ai_settings


class EmbeddingService:

    def __init__(self):
        self._model = None

    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(
                ai_settings.EMBEDDING_MODEL
            )
        return self._model


    def create_embedding(
        self,
        text: str
    ):

        if not text:
            raise ValueError(
                "Text cannot be empty"
            )

        try:
            embedding = self.model.encode(
                text,
                normalize_embeddings=True
            )
            return embedding.tolist()
        except Exception:
            from app.ai.rag.kb_vector_engine import kb_engine
            return kb_engine._compute_tfidf_vector(text).tolist()


embedding_service = EmbeddingService()
