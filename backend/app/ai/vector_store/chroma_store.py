import chromadb


class ChromaStore:

    def __init__(self):

        self.client = chromadb.PersistentClient(
            path="./storage/vector_db"
        )

        self.collection = (
            self.client.get_or_create_collection(
                name="resume_screening"
            )
        )

    def add_document(
        self,
        document_id: str,
        text: str,
        embedding: list[float],
        metadata: dict
    ):

        self.collection.upsert(
            ids=[document_id],
            documents=[text],
            embeddings=[embedding],
            metadatas=[metadata]
        )

    def search(
        self,
        embedding: list[float],
        top_k: int = 5
    ):

        return self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k
        )


chroma_store = ChromaStore()