from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.ai.chatbot.chatbot_service import ask_chatbot
from app.core.security import get_current_user
from app.models.database import get_db
from app.models.resume_tables import User
from app.services.chatbot_personal import get_user_latest_screening

router = APIRouter(
    prefix="/chatbot",
    tags=["Chatbot"]
)


class ChatbotRequest(BaseModel):
    question: str


class ChatbotResponse(BaseModel):
    answer: str


@router.post("/ask", response_model=ChatbotResponse)
def ask_chatbot_api(
    request: ChatbotRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    personal_result = get_user_latest_screening(
        db,
        current_user.user_id
    )

    answer = ask_chatbot(
        request.question,
        personal_result
    )

    return ChatbotResponse(
        answer=answer
    )