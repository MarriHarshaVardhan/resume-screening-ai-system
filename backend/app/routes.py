from fastapi import APIRouter

from app.api.authentication import (router as authentication_router)
from app.api.recent_screening import router as screening_router
router = APIRouter()

router.include_router(authentication_router)
router.include_router(screening_router, prefix="/api")