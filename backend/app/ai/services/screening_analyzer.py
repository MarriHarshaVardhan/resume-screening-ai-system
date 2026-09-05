import json
import logging
from groq import Groq
from app.core.config import settings

logger = logging.getLogger(__name__)

def analyze_screening(resume_text: str, job_title: str, required_skills: list[str]):
    client = Groq(api_key=settings.GROQ_API_KEY)
    prompt = f"""
You are an AI resume screening system.

Analyze the candidate resume against the given job requirements.

Job Title:
{job_title}

Required Skills:
{json.dumps(required_skills)}

Candidate Resume:
{resume_text}

Return ONLY valid JSON with this exact structure:
{{
  "matched_skills": ["skill1", "skill2"],
  "missing_skills": ["skill1", "skill2"],
  "match_score": 85.5,
  "screening_result": "SHORTLISTED",
  "recommendation": "Short explanation of why the candidate is suitable."
}}

Rules:
- matched_skills must contain only required skills supported by the resume.
- missing_skills must contain required skills not sufficiently supported by the resume.
- match_score must be between 0 and 100.
- screening_result must be one of: "SHORTLISTED", "REJECTED", "REVIEW".
- Base the decision only on the provided resume and requirements.
"""
    try:
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional AI resume screening engine. Return only valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )
        result = json.loads(response.choices[0].message.content)
        logger.info("Resume screening analysis completed")
        return result
    except Exception:
        logger.exception("Groq screening analysis failed")
        raise