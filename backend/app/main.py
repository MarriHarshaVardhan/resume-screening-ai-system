import logging

from fastapi import FastAPI

from app.routes import router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


app = FastAPI(
    title="AI Resume Screening API",
    version="1.0.0"
)


app.include_router(router)


@app.get("/v1")
def root():

    return {
        "message": "AI Resume Screening API is running"
    }