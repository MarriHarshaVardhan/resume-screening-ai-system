from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    DB_TYPE: str = "postgres"

    # JWT Authentication
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Resume Upload
    UPLOAD_DIRECTORY: str = "uploads"
    MAX_RESUME_FILE_SIZE: int = 10485760  # 10 MB in bytes
    ALLOWED_EXTENSIONS: str = ".pdf,.doc,.docx"

    # Groq LLM
    GROQ_API_KEY: str
    GROQ_MODEL: str = "openai/gpt-oss-20b"
    GROQ_TIMEOUT: float = 10.0
    GROQ_TEMPERATURE: float = 0.0



    # Sentence Transformer Embedding
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # Pinecone Vector DB
    PINECONE_API_KEY: str = ""
    PINECONE_ENVIRONMENT: str = "us-east-1"
    PINECONE_INDEX_NAME: str = "resume-kb-index"
    PINECONE_VECTOR_DIMENSION: int = 384
    PINECONE_METRIC: str = "cosine"
    PINECONE_CLOUD: str = "aws"
    PINECONE_REGION: str = "us-east-1"

    # RAG / Vector search
    RAG_TOP_K: int = 5
    TFIDF_MAX_FEATURES: int = 5000
    TFIDF_NGRAM_MIN: int = 1
    TFIDF_NGRAM_MAX: int = 2
    CHUNK_SIZE: int = 250
    CHUNK_OVERLAP: int = 50

    # AI Scoring thresholds
    SCORE_SELECTED_THRESHOLD: float = 75.0
    SCORE_SHORTLISTED_THRESHOLD: float = 50.0
    SCORE_SKILL_WEIGHT: float = 0.6
    SCORE_TEXT_WEIGHT: float = 0.4

    # CORS
    ALLOWED_ORIGINS: str = "*"

    # App metadata
    APP_TITLE: str = "AI Resume Screener API"
    APP_VERSION: str = "1.0.0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def get_allowed_origins(self) -> List[str]:
        if self.ALLOWED_ORIGINS == "*":
            return ["*"]
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    def get_allowed_extensions(self) -> set:
        return {e.strip() for e in self.ALLOWED_EXTENSIONS.split(",") if e.strip()}


settings = Settings()
