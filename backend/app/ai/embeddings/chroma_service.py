import chromadb

from app.ai.embeddings.embedding_service import get_embedding


# ChromaDB client create cheyyadam
client = chromadb.Client()


# Resume collection create cheyyadam
collection = client.get_or_create_collection(
    name="resume_collection"
)


def add_resume(resume_id: str, resume_text: str):
    """
    Resume text ni embedding ga convert chesi
    ChromaDB lo store chestundi.
    """

    embedding = get_embedding(resume_text)

    collection.add(
        ids=[resume_id],
        documents=[resume_text],
        embeddings=[embedding],
    )


def search_resumes(query: str, n_results: int = 5):
    """
    Query text ki semantic ga similar resumes ni
    ChromaDB nundi retrieve chestundi.
    """

    query_embedding = get_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
    )

    return results