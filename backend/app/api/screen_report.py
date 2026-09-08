from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.services.screen_report import (
    get_screening_result,
    generate_screening_report,
)
from app.dto.screen_report import ScreeningResultResponse

router = APIRouter(
    prefix="/screening-result",
    tags=["Screening Result"],
)

@router.get(
    "/{screening_id}",
    response_model=ScreeningResultResponse,
)
def view_screening_result(
    screening_id: int,
    db: Session = Depends(get_db),
):
    result = get_screening_result(
        db=db,
        screening_id=screening_id,
    )

    return {
        "screening_id": result.screening_id,
        "candidate_name": result.user.name if result.user else None,
        "job_title": result.job.job_title if result.job else None,
        "match_score": result.match_score,
        "matched_skills": result.matched_skills or [],
        "missing_skills": result.missing_skills or [],
        "experience": result.resume.experience if result.resume else None,
        "qualification": result.resume.qualification if result.resume else None,
        "certifications": result.resume.certifications if result.resume else [],
        "experience_assessment": result.experience_assessment,
        "qualification_assessment": result.qualification_assessment,
        "strengths": result.strengths or [],
        "concerns": result.concerns or [],
        "score_breakdown": result.score_breakdown or {},
        "recommendation": result.recommendation,
        "summary": result.screening_result,
    }

@router.get(
    "/{screening_id}/download",
)
def download_screening_report(
    screening_id: int,
    db: Session = Depends(get_db),
):
    pdf_file = generate_screening_report(
        db=db,
        screening_id=screening_id,
    )

    return StreamingResponse(
        pdf_file,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f'attachment; filename="screening_report_{screening_id}.pdf"'
            )
        },
    )