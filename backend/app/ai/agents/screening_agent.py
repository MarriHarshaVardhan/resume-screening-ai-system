import json
import logging

from app.ai.services.embedding_service import generate_embedding
from app.ai.services.pinecone_service import get_pinecone_index
from app.core.config import settings
from groq import Groq

logger = logging.getLogger(__name__)

client = Groq(api_key=settings.GROQ_API_KEY)

def retrieve_job_knowledge(job_title: str, query: str):
    embedding = generate_embedding(query)
    index = get_pinecone_index()

    response = index.query(
        vector=embedding,
        top_k=10,
        include_metadata=True,
        filter={
            "job_title": {
                "$eq": job_title
            }
        }
    )

    knowledge = []

    for match in response.get("matches", []):
        metadata = match.get("metadata", {})
        text = metadata.get("text")

        if text:
            knowledge.append(text)

    return knowledge

def run_screening_agent(
    resume_text: str,
    resume_id: int,
    job_title: str,
    required_skills: list[str]
):
    if not resume_text.strip():
        raise ValueError("Resume text cannot be empty")

    query = f"""
Evaluate the requirements, responsibilities, skills and qualifications
needed for the role of {job_title}.
Required skills: {", ".join(required_skills)}
"""

    job_knowledge = retrieve_job_knowledge(job_title, query)

    if not job_knowledge:
        raise ValueError("No relevant job knowledge found")

    jd_context = "\n\n".join(job_knowledge)
    required_skills_text = ", ".join(required_skills)

    prompt = f"""
You are an AI resume screening agent.

Evaluate the candidate resume against the job requirements retrieved
from the knowledge base and the required skills provided for the role.

JOB TITLE:
{job_title}

REQUIRED SKILLS:
{required_skills_text}

JOB REQUIREMENTS FROM KNOWLEDGE BASE:
{jd_context}

CANDIDATE RESUME:
{resume_text}

Return ONLY valid JSON with this exact structure:

{{
  "matched_skills": [],
  "missing_skills": [],
  "match_score": 0,
  "screening_result": "REVIEW",
  "experience_assessment": "",
  "qualification_assessment": "",
  "strengths": [],
  "concerns": [],
  "score_breakdown": {{
    "skills": 0,
    "experience": 0,
    "qualification": 0,
    "overall_fit": 0
  }},
  "recommendation": ""
}}

Rules:
- match_score must be between 0 and 100.
- score_breakdown values must be between 0 and 100.
- matched_skills must contain skills supported by the resume.
- missing_skills must contain important required skills or requirements not supported by the resume.
- Evaluate both required_skills and the retrieved job knowledge.
- experience_assessment must assess the candidate's relevant experience.
- qualification_assessment must assess relevant qualifications based only on available resume information.
- strengths must contain the candidate's strongest relevant points.
- concerns must contain important gaps or risks.
- screening_result must be one of: SHORTLISTED, REVIEW, REJECTED.
- recommendation must briefly explain the final decision.
- Do not invent experience, qualifications or skills that are not supported by the resume.
- Do not include markdown.
"""

    try:
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional AI resume screening agent."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        content = response.choices[0].message.content.strip()
        result = json.loads(content)

        logger.info(
            "Screening agent completed: resume_id=%s job_title=%s",
            resume_id,
            job_title
        )

        return result

    except json.JSONDecodeError:
        logger.exception("Groq returned invalid JSON")
        raise ValueError("AI screening returned invalid response")
    except Exception:
        logger.exception("Screening agent failed")
        raise