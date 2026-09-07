import logging

from app.core.security import get_current_user
from app.dto.knowledge import KnowledgeAddDTO
from app.models.resume_tables import User
from app.services.knowledge_add import add_knowledge
from fastapi import APIRouter, Depends

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/knowledge", tags=["Knowledge"])

@router.post("/add")
def add_knowledge_api(
    data: KnowledgeAddDTO,
    current_user: User = Depends(get_current_user)
):
    logger.info("POST /knowledge/add called by user_id=%s", current_user.user_id)
    return add_knowledge(data=data, current_user=current_user)