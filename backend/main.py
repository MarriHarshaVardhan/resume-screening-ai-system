from fastapi import FastAPI
from fastapi.security import HTTPBearer

from app.models.database import Base, engine
from app.models.resume_tables import User
from app.routes import router


# Create database tables
Base.metadata.create_all(bind=engine)


security = HTTPBearer()

app = FastAPI(
    title="AI Resume Screener API",
    version="1.0.0",
)


app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "AI Resume Screener API is running"
    }
