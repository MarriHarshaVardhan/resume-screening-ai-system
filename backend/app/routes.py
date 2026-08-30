from fastapi import APIRouter

from app.api.login import router as login_router
from app.api.resume_upload import router as resume_upload_router


router = APIRouter()


router.include_router(login_router)

router.include_router(resume_upload_router)