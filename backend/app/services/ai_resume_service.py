from sqlalchemy.orm import Session

from app.ai.resume.resume_parser import parse_resume
from app.models.resume_tables import Resume


def process_resume(
    db: Session,
    user_id: int,
    file_name: str,
    file_path: str,
    resume_text: str
):

  
    parsed_resume = parse_resume(
        resume_text
    )

    
    resume = Resume(
        user_id=user_id,
        resume_file_name=file_name,
        resume_file_path=file_path,
        resume_text=resume_text,

        skills=parsed_resume.skills,

        experience=parsed_resume.experience,

        qualification=(
            parsed_resume.qualifications
        ),

        certifications=(
            parsed_resume.certifications
        )
    )

    
    db.add(resume)

    db.commit()

    db.refresh(resume)

    return {
        "resume_id": resume.resume_id,

        "candidate_name": (
            parsed_resume.candidate_name
        ),

        "email": parsed_resume.email,

        "phone": parsed_resume.phone,

        "skills": parsed_resume.skills,

        "experience": parsed_resume.experience,

        "qualifications": (
            parsed_resume.qualifications
        ),

        "certifications": (
            parsed_resume.certifications
        ),

        "projects": parsed_resume.projects
    }