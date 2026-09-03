from app.ai.embeddings.embedding_service import (
    embedding_service
)


text = """
Python developer with FastAPI,
PostgreSQL and machine learning experience.
"""


embedding = embedding_service.create_embedding(
    text
)


print(
    "Embedding dimensions:",
    len(embedding)
)

print(
    "First values:",
    embedding[:5]
)
