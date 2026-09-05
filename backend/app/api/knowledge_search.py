import logging
from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.dto.knowledge import KnowledgeSearchDTO
from app.models.resume_tables import User
from app.services.knowledge_search import search_knowledge

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/knowledge", tags=["Knowledge"])

@router.post("/search")
def search_knowledge_api(
    data: KnowledgeSearchDTO,
    current_user: User = Depends(get_current_user)
):
    logger.info("POST /knowledge/search called by user_id=%s", current_user.user_id)
    return search_knowledge(data=data, current_user=current_user)