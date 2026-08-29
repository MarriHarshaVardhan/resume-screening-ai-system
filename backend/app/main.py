from fastapi import FastAPI

from app.models.database import (
    Base,
    engine
)

from app.models.resume_tables import User

from app.routes import router

Base.metadata.create_all(
    bind=engine
)

app = FastAPI(
    title="AI Resume Screener API",
    version="1.0.0"
)

app.include_router(
    router
)

@app.get("/")
def root():

    return {
        "message": "AI Resume Screener API is running"
    }
