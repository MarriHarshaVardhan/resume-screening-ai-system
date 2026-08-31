from fastapi import APIRouter

from app.api.authentication import router as authentication_router
from app.api.recent_screening import router as screening_router
from app.api.screening_history import router as screening_history_router
from app.api.resume_upload import router as resume_upload_router
from app.api.screening_progress import router as screening_progress_router

router = APIRouter()

router.include_router(authentication_router)
router.include_router(resume_upload_router)
router.include_router(screening_progress_router)
router.include_router(screening_router, prefix="/api")
router.include_router(screening_history_router)