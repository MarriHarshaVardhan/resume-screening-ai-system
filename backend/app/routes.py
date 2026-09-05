from app.api.authentication import router as authentication_router
from app.api.knowledge_add import router as knowledge_add_router
from app.api.knowledge_search import router as knowledge_search_router
from app.api.knowledge_upload import router as knowledge_upload_router
from app.api.recent_screening import router as screening_router
from app.api.resume_analysis import router as resume_analysis_router
from app.api.resume_cleaning import router as resume_cleaning_router
from app.api.resume_extraction import router as resume_extraction_router
from app.api.resume_upload import router as resume_upload_router
from app.api.screen_report import router as screen_report_router
from app.api.screen_view import router as screen_view_router
from app.api.screening_agent import router as screening_agent_router
from app.api.screening_history import router as screening_history_router
from app.api.start_screening import router as start_screening_router
from fastapi import APIRouter

router = APIRouter()

router.include_router(authentication_router)
router.include_router(resume_upload_router)
router.include_router(knowledge_upload_router)
router.include_router(knowledge_search_router)
router.include_router(screening_router, prefix="/api")
router.include_router(screening_history_router)
router.include_router(screen_view_router)
router.include_router(screen_report_router)
router.include_router(resume_extraction_router)
router.include_router(resume_cleaning_router)
router.include_router(resume_analysis_router)
router.include_router(start_screening_router)
router.include_router(knowledge_add_router)
router.include_router(screening_agent_router, prefix="/api")