import json

from app.ai.job.job_schema import JobSchema
from app.ai.llm.groq_client import groq_client
from app.ai.llm.prompts import JOB_EXTRACTION_PROMPT


def parse_job(
    job_description: str
) -> JobSchema:

    if not job_description:
        raise ValueError(
            "Job description cannot be empty"
        )

    prompt = JOB_EXTRACTION_PROMPT.format(
        job_description=job_description
    )

    response = groq_client.generate(
        prompt=prompt,
        temperature=0.0
    )

    try:

        data = json.loads(response)

    except json.JSONDecodeError as error:

        raise ValueError(
            f"Invalid JSON returned by Groq: {response}"
        ) from error

    return JobSchema.model_validate(data)