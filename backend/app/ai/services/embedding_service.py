import logging

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

MODEL_NAME = "BAAI/bge-small-en-v1.5"
model = SentenceTransformer(MODEL_NAME)

def generate_embedding(text: str) -> list[float]:
    if not text.strip():
        raise ValueError("Text cannot be empty")
    embedding = model.encode(text, normalize_embeddings=True)
    logger.info("Embedding generated successfully")
    return embedding.tolist()