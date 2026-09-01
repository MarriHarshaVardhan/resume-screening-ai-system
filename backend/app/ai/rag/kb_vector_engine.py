import logging
import re
from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.core.config import settings

logger = logging.getLogger(__name__)


class VectorKnowledgeBase:
    """
    RAG Vector Knowledge Base for indexing resume text, chunking,
    and performing vector similarity retrieval against Job Descriptions.
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(settings.TFIDF_NGRAM_MIN, settings.TFIDF_NGRAM_MAX),
            max_features=settings.TFIDF_MAX_FEATURES
        )
        self.doc_chunks: List[Dict[str, Any]] = []

    def chunk_text(
        self,
        text: str,
        chunk_size: int | None = None,
        overlap: int | None = None
    ) -> List[str]:
        """
        Split text into overlapping sentence/word chunks.
        """
        chunk_size = chunk_size or settings.CHUNK_SIZE
        overlap = overlap or settings.CHUNK_OVERLAP

        if not text:
            return []

        words = text.split()
        if len(words) <= chunk_size:
            return [text]

        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
            if i + chunk_size >= len(words):
                break

        return chunks

    def _compute_tfidf_vector(self, text: str) -> np.ndarray:
        """
        Compute TF-IDF vector array for a given text.
        """
        if not text:
            return np.zeros(settings.PINECONE_VECTOR_DIMENSION)
        try:
            vec = self.vectorizer.fit_transform([text]).toarray()[0]
            return vec
        except Exception:
            return np.zeros(settings.PINECONE_VECTOR_DIMENSION)

    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute TF-IDF cosine similarity score between two text strings (0.0 to 100.0).
        """

        if not text1 or not text2:
            return 0.0

        try:
            tfidf_matrix = self.vectorizer.fit_transform([text1, text2])
            sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(np.round(sim * 100.0, 2))
        except Exception as e:
            logger.warning("Vector similarity computation fallback: %s", e)
            return self._jaccard_similarity(text1, text2)

    def _jaccard_similarity(self, text1: str, text2: str) -> float:
        set1 = set(re.findall(r"\w+", text1.lower()))
        set2 = set(re.findall(r"\w+", text2.lower()))
        if not set1 or not set2:
            return 0.0
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        return float(np.round((len(intersection) / len(union)) * 100.0, 2))

    def rag_skill_match(
        self,
        resume_skills: List[str],
        required_skills: List[str],
        resume_text: str,
        job_description: str
    ) -> Tuple[List[str], List[str], float]:
        """
        Perform RAG vector & keyword matching between candidate skills/resume and job requirements.
        Returns: (matched_skills, missing_skills, vector_match_score)
        """
        resume_text_lower = (resume_text or "").lower()
        resume_skills_lower = set(s.lower() for s in (resume_skills or []))

        matched = []
        missing = []

        for req in (required_skills or []):
            req_lower = req.lower()
            # Direct or substring/word match in extracted skills or full text
            if req_lower in resume_skills_lower or req_lower in resume_text_lower:
                matched.append(req)
            else:
                missing.append(req)

        # Semantic Vector Score between full resume text & job description
        text_score = self.compute_similarity(resume_text, job_description)

        # Skill ratio score
        if required_skills:
            skill_score = (len(matched) / len(required_skills)) * 100.0
        else:
            skill_score = text_score

        # Composite score weighting from config (default: 60% skills + 40% vector)
        skill_weight = settings.SCORE_SKILL_WEIGHT
        text_weight = settings.SCORE_TEXT_WEIGHT
        composite_score = float(np.round((skill_score * skill_weight) + (text_score * text_weight), 2))
        composite_score = min(100.0, max(0.0, composite_score))

        return matched, missing, composite_score


# Global KB Vector Engine instance
kb_engine = VectorKnowledgeBase()
