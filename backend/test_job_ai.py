from app.ai.job.job_parser import parse_job


job_description = """
We are looking for an AI Full Stack Developer.

Required skills:
Python
FastAPI
Flutter
PostgreSQL
Machine Learning
LLM
RAG

Experience:
2+ years

Qualification:
B.Tech or equivalent
"""


result = parse_job(
    job_description
)


print(
    result.model_dump_json(
        indent=4
    )
)