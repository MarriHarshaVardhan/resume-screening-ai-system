from contextlib import asynccontextmanager

from app.core.config import settings
from app.models.database import Base, engine
from app.routes import router
from fastapi import FastAPI

Base.metadata.create_all(
    bind=engine
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    router
)


@app.get("/", include_in_schema=False)
def root():

    return {
        "message": f"{settings.APP_TITLE} is running"
    }