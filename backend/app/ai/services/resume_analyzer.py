import json
import logging

from groq import Groq

from app.core.config import settings


logger = logging.getLogger(__name__)


def analyze_resume_with_groq(cleaned_resume_text: str) -> dict:
    client = Groq(api_key=settings.GROQ_API_KEY)

    prompt = f"""
You are an AI resume information extraction system.

Extract the following information from the resume.

1. Skills
2. Total professional experience
3. Highest qualification
4. Certifications

Return only valid JSON in this exact format:

{{
    "skills": ["skill1", "skill2"],
    "experience": "X years",
    "qualification": "qualification name",
    "certifications": ["certification1", "certification2"]
}}

Rules:
- Extract only information present in the resume.
- Do not invent skills, experience, qualifications, or certifications.
- Normalize skill names where appropriate.
- If no certifications are found, return an empty list.
- If experience cannot be determined, return null.
- If qualification cannot be determined, return null.

Resume:

{cleaned_resume_text}
"""

    try:
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You extract structured information from resumes "
                        "and return valid JSON only."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError("Groq returned an empty response")

        return json.loads(content)

    except Exception:
        logger.exception("Groq resume analysis failed")
        raise