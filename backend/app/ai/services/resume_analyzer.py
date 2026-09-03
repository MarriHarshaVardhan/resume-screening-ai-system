import json
import logging
import re

from groq import Groq
from app.core.config import settings

logger = logging.getLogger(__name__)


def _extract_fallback_resume_info(text: str) -> dict:
    common_skills = [
        "Python", "Java", "C++", "JavaScript", "TypeScript", "React", "Node.js",
        "FastAPI", "Django", "Flask", "PostgreSQL", "MySQL", "MongoDB", "Docker",
        "Kubernetes", "AWS", "Machine Learning", "Deep Learning", "NLP", "RAG",
        "Data Structures", "SQL", "Git"
    ]
    found_skills = []
    text_upper = (text or "").upper()
    for s in common_skills:
        if s.upper() in text_upper:
            found_skills.append(s)

    exp_match = re.search(r"(\d+\+?\s*(?:years?|yrs?))", text or "", re.IGNORECASE)
    experience = exp_match.group(1) if exp_match else "1+ years"

    qual_match = re.search(r"(B\.?Tech|M\.?Tech|B\.?S|M\.?S|Ph\.?D|Bachelor|Master)", text or "", re.IGNORECASE)
    qualification = qual_match.group(1) if qual_match else "Bachelor's Degree"

    return {
        "skills": found_skills or ["Python", "Software Engineering"],
        "experience": experience,
        "qualification": qualification,
        "certifications": []
    }


def analyze_resume_with_groq(cleaned_resume_text: str) -> dict:
    groq_key = settings.GROQ_API_KEY
    if not groq_key or groq_key.startswith("your-") or "key" in groq_key.lower():
        return _extract_fallback_resume_info(cleaned_resume_text)

    # Clean null bytes and limit text to avoid TPM token overflow
    safe_text = (cleaned_resume_text or "").replace("\x00", "")[:6000]

    try:
        client = Groq(api_key=groq_key, timeout=settings.GROQ_TIMEOUT)
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

Resume:

{safe_text}
"""

        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You extract structured information from resumes and return valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=settings.GROQ_TEMPERATURE,
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError("Groq returned an empty response")

        return json.loads(content)

    except Exception as e:
        logger.warning("Groq resume analysis fallback triggered: %s", e)
        return _extract_fallback_resume_info(cleaned_resume_text)