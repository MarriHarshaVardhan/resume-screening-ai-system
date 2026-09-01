from app.ai.vector_store.pinecone_store import pinecone_kb


def index_resume(
    resume_id: int,
    resume_text: str,
    user_id: int
):
    pinecone_kb.upsert_resume_vector(
        resume_id=resume_id,
        text=resume_text,
        metadata={
            "resume_id": str(resume_id),
            "user_id": str(user_id)
        }
    )
    return True