from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parent
FAQ_FILE = BASE_DIR / "faq.md"
CHROMA_DIR = BASE_DIR / "chroma_db"

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path=str(CHROMA_DIR))

collection = client.get_or_create_collection(
    name="resume_screening_faq"
)


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

    ids = [f"faq_{index}" for index in range(len(chunks))]

    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings
    )

    print(f"Stored {len(chunks)} FAQ chunks in ChromaDB.")


if __name__ == "__main__":
    create_faq_embeddings()