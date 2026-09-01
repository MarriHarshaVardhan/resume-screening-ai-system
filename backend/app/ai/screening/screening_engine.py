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

    prompt = SCREENING_PROMPT.format(
        resume_text=resume_text,
        job_requirements=job_requirements
    )

    response = groq_client.generate(
        prompt=prompt,
        temperature=0.0
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