from groq import Groq
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

from app.core.config import settings

model = SentenceTransformer("all-MiniLM-L6-v2")

pc = Pinecone(
    api_key=settings.PINECONE_API_KEY
)

index = pc.Index(
    settings.PINECONE_INDEX_NAME
)

groq_client = Groq(
    api_key=settings.GROQ_API_KEY
)


def get_relevant_faq(question: str):
    embedding = model.encode(question).tolist()

    result = index.query(
        vector=embedding,
        top_k=1,
        include_metadata=True
    )

    if not result.matches:
        return ""

    return result.matches[0].metadata["text"]


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