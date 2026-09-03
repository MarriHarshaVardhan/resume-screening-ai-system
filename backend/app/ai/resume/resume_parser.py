import json

from app.ai.llm.groq_client import groq_client
from app.ai.llm.prompts import RESUME_EXTRACTION_PROMPT
from app.ai.resume.resume_schema import ResumeSchema


def parse_resume(resume_text: str) -> ResumeSchema:

    if not resume_text:
        raise ValueError(
            "Resume text cannot be empty"
        )

    prompt = RESUME_EXTRACTION_PROMPT.format(
        resume_text=resume_text
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

    return ResumeSchema.model_validate(data)