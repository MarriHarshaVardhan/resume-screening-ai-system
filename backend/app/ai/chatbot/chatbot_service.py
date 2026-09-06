from pathlib import Path

import chromadb
from groq import Groq
from sentence_transformers import SentenceTransformer

from app.core.config import settings

BASE_DIR = Path(__file__).resolve().parent
CHROMA_DIR = BASE_DIR / "chroma_db"

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path=str(CHROMA_DIR))

collection = client.get_collection(
    name="resume_screening_faq"
)

groq_client = Groq(
    api_key=settings.GROQ_API_KEY
)


def get_relevant_faq(question: str):
    embedding = model.encode([question]).tolist()

    result = collection.query(
        query_embeddings=embedding,
        n_results=1
    )

    return result["documents"][0][0]


def ask_chatbot(
    question: str,
    personal_result: dict | None = None
):
    faq_context = get_relevant_faq(question)

    personal_context = ""

    if personal_result:
        personal_context = (
            f"Personal Screening Data:\n"
            f"{personal_result}\n"
        )

    response = groq_client.chat.completions.create(
        model=settings.GROQ_MODEL,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an AI Resume Screening assistant. "
                    "Answer the user's question using the provided FAQ context "
                    "and personal screening data when available. "
                    "For personal questions, use the personal screening data. "
                    "Do not invent information. "
                    "If the required information is not available, say that "
                    "you do not have enough information."
                )
            },
            {
                "role": "user",
                "content": (
                    f"FAQ Context:\n{faq_context}\n\n"
                    f"{personal_context}\n"
                    f"User Question:\n{question}"
                )
            }
        ]
    )

    return response.choices[0].message.content