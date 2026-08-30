from fastapi import APIRouter

from app.api.authentication import (router as authentication_router)

router = APIRouter()

router.include_router(authentication_router)
