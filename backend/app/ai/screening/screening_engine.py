import json

from app.ai.llm.groq_client import groq_client
from app.ai.llm.prompts import SCREENING_PROMPT
from app.ai.screening.screening_schema import (
    ScreeningResultSchema
)


def screen_resume(
    resume_text: str,
    job_requirements: str
) -> ScreeningResultSchema:

    safe_resume = (resume_text or "").replace("\x00", "")[:6000]
    safe_job = (job_requirements or "").replace("\x00", "")[:3000]

    prompt = SCREENING_PROMPT.format(
        resume_text=safe_resume,
        job_requirements=safe_job
    )

    response = groq_client.generate(
        prompt=prompt
    )


    try:

        result = json.loads(response)

    except json.JSONDecodeError as error:

        raise ValueError(
            "Groq returned invalid screening JSON"
        ) from error

    return ScreeningResultSchema.model_validate(
        result
    )