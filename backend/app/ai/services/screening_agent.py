import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.core.config import settings
from app.ai.parsers.pdf_parser import extract_text_from_pdf
from app.ai.parsers.docx_parser import extract_text_from_docx
from app.ai.preprocessors.text_cleaner import clean_resume_text
from app.ai.services.resume_analyzer import analyze_resume_with_groq
from app.ai.rag.kb_vector_engine import kb_engine
from app.models.resume_tables import Resume, Job, ScreeningResult, User

logger = logging.getLogger(__name__)


class AIScreeningAgent:
    """
    End-to-End AI Agent for extracting resume text, preprocessing,
    vectorizing into Knowledge Base, matching against Job Descriptions via RAG,
    calculating scores, and populating Screening History in the database.
    """

    def process_and_extract_resume(self, db: Session, resume: Resume) -> str:
        """
        Extract text from file, clean it, and store extracted text in DB.
        """
        file_path = resume.resume_file_path
        ext = (resume.resume_file_name or "").lower()

        extracted_text = ""
        allowed_ext = settings.get_allowed_extensions()
        if ext.endswith(".pdf"):
            extracted_text = extract_text_from_pdf(file_path)
        elif ext.endswith(".docx"):
            extracted_text = extract_text_from_docx(file_path)
        else:
            extracted_text = resume.resume_text or ""

        extracted_text = (extracted_text or "").replace("\x00", "")
        cleaned_text = clean_resume_text(extracted_text) if extracted_text else ""
        cleaned_text = (cleaned_text or "").replace("\x00", "")

        resume.resume_text = extracted_text
        resume.cleaned_resume_text = cleaned_text

        # Try Groq AI analysis if available or extract structured info
        try:
            analysis = analyze_resume_with_groq(cleaned_text)
            resume.skills = [str(s).replace("\x00", "") for s in (analysis.get("skills") or [])]
            resume.experience = str(analysis.get("experience") or "").replace("\x00", "") if analysis.get("experience") else None
            resume.qualification = str(analysis.get("qualification") or "").replace("\x00", "") if analysis.get("qualification") else None
            resume.certifications = [str(c).replace("\x00", "") for c in (analysis.get("certifications") or [])]
        except Exception as e:
            logger.warning("Groq AI analysis skipped/fallback: %s", e)

        db.commit()
        db.refresh(resume)
        return cleaned_text or extracted_text


    def screen_resume_against_job(
        self,
        db: Session,
        resume_id: int,
        job_id: int
    ) -> ScreeningResult:
        """
        Execute RAG vector screening between Resume and Job Description.
        Calculates vector match scores, identifies matched/missing skills,
        generates AI recommendation, and updates/creates ScreeningResult in DB.
        """
        resume = db.query(Resume).filter(Resume.resume_id == resume_id).first()
        if not resume:
            raise ValueError(f"Resume {resume_id} not found")

        job = db.query(Job).filter(Job.job_id == job_id).first() if job_id else None
        if not job:
            job = db.query(Job).order_by(Job.created_at.desc()).first()

        if not job:
            # No job found — raise an error so callers know no job exists
            raise ValueError(
                "No job description found in the database. "
                "Please create a job before running screening."
            )

        # Ensure resume text is extracted and cleaned
        resume_text = resume.cleaned_resume_text or resume.resume_text
        if not resume_text:
            resume_text = self.process_and_extract_resume(db, resume)

        resume_skills = resume.skills or []
        required_skills = job.required_skills or []

        # Index resume into Pinecone Vector DB Knowledge Base
        try:
            from app.ai.vector_store.pinecone_store import pinecone_kb
            pinecone_kb.upsert_resume_vector(
                resume_id=resume.resume_id,
                text=resume_text,
                metadata={"user_id": resume.user_id, "job_title": job.job_title}
            )
            matched_skills, missing_skills, score = pinecone_kb.query_kb_vectors(
                resume_skills=resume_skills,
                required_skills=required_skills,
                resume_text=resume_text or "",
                job_description=job.job_description or ""
            )
        except Exception as pe:
            logger.warning("Pinecone KB integration fallback: %s", pe)
            matched_skills, missing_skills, score = kb_engine.rag_skill_match(
                resume_skills=resume_skills,
                required_skills=required_skills,
                resume_text=resume_text or "",
                job_description=job.job_description or ""
            )

        # Recommendation & status evaluation using configurable thresholds
        selected_threshold = settings.SCORE_SELECTED_THRESHOLD
        shortlisted_threshold = settings.SCORE_SHORTLISTED_THRESHOLD

        if score >= selected_threshold:
            status_str = "Selected"
            recommendation = f"Strong candidate match ({score}%). Possesses key skills: {', '.join(matched_skills[:4])}."
        elif score >= shortlisted_threshold:
            status_str = "Shortlisted"
            recommendation = f"Moderate match ({score}%). Missing some required skills: {', '.join(missing_skills[:3])}."
        else:
            status_str = "Rejected"
            recommendation = f"Low match ({score}%). Lacks critical required skills for this role."

        # Check existing screening result or create new
        screening = db.query(ScreeningResult).filter(
            ScreeningResult.resume_id == resume.resume_id,
            ScreeningResult.job_id == job.job_id
        ).first()

        if not screening:
            screening = ScreeningResult(
                user_id=resume.user_id,
                resume_id=resume.resume_id,
                job_id=job.job_id,
                status=status_str,
                progress=100,
                matched_skills=matched_skills,
                missing_skills=missing_skills,
                match_score=score,
                screening_result=status_str,
                recommendation=recommendation
            )
            db.add(screening)
        else:
            screening.status = status_str
            screening.progress = 100
            screening.matched_skills = matched_skills
            screening.missing_skills = missing_skills
            screening.match_score = score
            screening.screening_result = status_str
            screening.recommendation = recommendation

        db.commit()
        db.refresh(screening)
        logger.info("AI Screening completed: screening_id=%s, score=%s", screening.screening_id, score)

        # Automatically update Daily Screening Analytics & Job Profiles in DB
        try:
            from datetime import datetime
            from app.models.resume_tables import DailyScreeningStats
            today_str = datetime.utcnow().strftime("%Y-%m-%d")
            stats = db.query(DailyScreeningStats).filter(DailyScreeningStats.date == today_str).first()
            total_resumes_count = db.query(Resume).count()

            if not stats:
                stats = DailyScreeningStats(
                    date=today_str,
                    total_resumes=total_resumes_count,
                    total_screenings=1,
                    selected_count=1 if status_str == "Selected" else 0,
                    shortlisted_count=1 if status_str == "Shortlisted" else 0,
                    rejected_count=1 if status_str == "Rejected" else 0,
                    job_profiles_summary={job.job_title: 1}
                )
                db.add(stats)
            else:
                stats.total_resumes = total_resumes_count
                stats.total_screenings += 1
                if status_str == "Selected":
                    stats.selected_count += 1
                elif status_str == "Shortlisted":
                    stats.shortlisted_count += 1
                elif status_str == "Rejected":
                    stats.rejected_count += 1

                summary = dict(stats.job_profiles_summary or {})
                summary[job.job_title] = summary.get(job.job_title, 0) + 1
                stats.job_profiles_summary = summary

            db.commit()
        except Exception as e:
            logger.warning("Daily stats update warning: %s", e)

        return screening


screening_agent = AIScreeningAgent()
