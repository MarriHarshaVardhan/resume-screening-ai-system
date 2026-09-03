# Re-export the central settings object under the `ai_settings` alias so that
# AI sub-modules can import it without creating a circular dependency on
# `app.core.config` directly.  All AI-specific settings (EMBEDDING_MODEL,
# GROQ_*, PINECONE_*, RAG_*, scoring thresholds …) live in Settings and are
# read from the .env file.

from app.core.config import settings as ai_settings

__all__ = ["ai_settings"]
