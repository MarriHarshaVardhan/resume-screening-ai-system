RESUME_EXTRACTION_PROMPT = """
You are an expert AI resume parser.

Extract structured information from the resume text.

IMPORTANT RULES:

1. Extract information ONLY from the provided resume.
2. Never invent information.
3. Never guess missing information.
4. If information does not exist, return null or [].
5. Return ONLY valid JSON.
6. Do not include markdown.
7. Do not include ```json.

Required JSON format:

{{
    "candidate_name": null,
    "email": null,
    "phone": null,
    "skills": [],
    "experience": [],
    "qualifications": [],
    "certifications": [],
    "projects": []
}}

Resume Text:

{resume_text}
"""
JOB_EXTRACTION_PROMPT = """
You are an expert AI job description parser.

Extract structured requirements from the job description.

IMPORTANT:

1. Extract only information present in the job description.
2. Never invent requirements.
3. Return only valid JSON.
4. Do not use markdown.

Return exactly:

{{
    "job_title": "",
    "required_skills": [],
    "required_experience": null,
    "required_qualifications": [],
    "required_certifications": []
}}

Job Description:

{job_description}
"""

SCREENING_PROMPT = """
You are an AI resume screening system.

Compare the resume against the job requirements.

Analyze:

1. Skill match
2. Experience match
3. Qualification match
4. Certification match
5. Semantic relevance

Return ONLY valid JSON.

Required format:

{{
    "matched_skills": [],
    "missing_skills": [],
    "experience_match": "",
    "qualification_match": "",
    "certification_match": "",
    "strengths": [],
    "weaknesses": [],
    "match_score": 0,
    "recommendation": "",
    "explanation": ""
}}

Resume:

{resume_text}

Job Requirements:

{job_requirements}
"""