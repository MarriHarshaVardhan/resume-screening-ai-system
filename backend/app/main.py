from contextlib import asynccontextmanager

from app.models.database import Base, engine
from app.routes import router
from fastapi import FastAPI

Base.metadata.create_all(
    bind=engine
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="AI Resume Screener API",
    version="1.0.0",
    lifespan=lifespan
)


app.include_router(
    router
)


@app.get("/")
def root():

    return {
        "message": "AI Resume Screener API is running"
    }