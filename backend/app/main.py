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


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI Resume Screener API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
        "message": "AI Resume Screener API is running"
    }