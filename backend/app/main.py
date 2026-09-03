from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models.database import Base, engine
from app.routes import router


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


# CORS - Flutter Web / Chrome connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include all API routes
app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "AI Resume Screener API is running"
    }