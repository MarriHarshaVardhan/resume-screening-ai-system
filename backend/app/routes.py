from app.api.authentication import router as authentication_router
from app.api.recent_screening import router as screening_router
from app.api.resume_cleaning import router as resume_cleaning_router
from app.api.resume_extraction import router as resume_extraction_router
from app.api.resume_upload import router as resume_upload_router
from app.api.screen_report import router as screen_report_router
from app.api.screen_view import router as screen_view_router
from app.api.screening_history import router as screening_history_router
from app.api.resume_analysis import router as resume_analysis_router
from app.api.ai_screening import router as ai_screening_router
from app.api.admin_dashboard import router as admin_dashboard_router
from app.mcp.mcp_server import router as mcp_router
from fastapi import APIRouter

router = APIRouter()

# Main Endpoints displayed cleanly in Swagger UI
router.include_router(authentication_router)
router.include_router(resume_upload_router)
router.include_router(screening_router, prefix="/api")
router.include_router(screening_history_router)
router.include_router(screen_report_router)
router.include_router(ai_screening_router)
router.include_router(admin_dashboard_router)

# Internal processing endpoints hidden from Swagger UI per user requirement
router.include_router(screen_view_router, include_in_schema=False)
router.include_router(resume_extraction_router, include_in_schema=False)
router.include_router(resume_cleaning_router, include_in_schema=False)
router.include_router(resume_analysis_router, include_in_schema=False)
router.include_router(mcp_router, include_in_schema=False)