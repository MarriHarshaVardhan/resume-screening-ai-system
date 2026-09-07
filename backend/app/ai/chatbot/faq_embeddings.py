from pathlib import Path

from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

from app.core.config import settings

BASE_DIR = Path(__file__).resolve().parent
FAQ_FILE = BASE_DIR / "faq.md"

model = SentenceTransformer("all-MiniLM-L6-v2")

pc = Pinecone(
    api_key=settings.PINECONE_API_KEY
)

index_name = settings.PINECONE_INDEX_NAME

if not pc.has_index(index_name):
    pc.create_index(
        name=index_name,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )

index = pc.Index(index_name)


def load_faq():
    content = FAQ_FILE.read_text(encoding="utf-8")

    sections = content.split("\n## ")

    chunks = []

    for section in sections:
        section = section.strip()

        if section and section != "# AI Resume Screening - Frequently Asked Questions":
            chunks.append(section)

    return chunks


def create_faq_embeddings():
    chunks = load_faq()

    embeddings = model.encode(chunks).tolist()

    records = []

    for index_number, (chunk, embedding) in enumerate(
        zip(chunks, embeddings)
    ):
        records.append(
            {
                "id": f"faq_{index_number}",
                "values": embedding,
                "metadata": {
                    "text": chunk
                }
            }
        )

    index.upsert(vectors=records)

    print(
        f"Stored {len(chunks)} FAQ chunks in Pinecone."
    )


if __name__ == "__main__":
    create_faq_embeddings()