import logging

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


logger = logging.getLogger(__name__)

_model = None


def get_model():
    global _model

    if _model is None:
        logger.info("Loading embedding model")
        _model = SentenceTransformer("all-MiniLM-L6-v2")

    return _model


def get_embedding(text: str):
    model = get_model()

    embedding = model.encode(text)

    return embedding


def calculate_similarity(text1: str, text2: str) -> float:
    embedding1 = get_embedding(text1)
    embedding2 = get_embedding(text2)

    similarity = cosine_similarity(
        [embedding1],
        [embedding2]
    )[0][0]

    return float(similarity)