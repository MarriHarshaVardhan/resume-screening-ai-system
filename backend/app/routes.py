from fastapi import APIRouter

from app.api.authentication import (router as authentication_router)
from app.api.screen_view import (router as screen_view_router)
from app.api.screen_report import (router as screen_report_router)

router = APIRouter()

router.include_router(authentication_router)
router.include_router(screen_view_router)
router.include_router(screen_report_router)
