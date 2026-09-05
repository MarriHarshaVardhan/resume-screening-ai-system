from io import BytesIO
from xml.sax.saxutils import escape
from fastapi import HTTPException, status
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy.orm import Session
from app.models.resume_tables import ScreeningResult

def get_screening_result(
    db: Session,
    screening_id: int,
):
    result = (
        db.query(ScreeningResult)
        .filter(
            ScreeningResult.screening_id == screening_id
        )
        .first()
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Screening result not found",
        )

    return result

def _format_value(value):
    if value is None:
        return "Not available"

    if isinstance(value, list):
        if not value:
            return "None"
        return ", ".join(str(item) for item in value)

    if isinstance(value, dict):
        if not value:
            return "None"
        return ", ".join(
            f"{key}: {value}"
            for key, value in value.items()
        )

    return str(value)

def generate_screening_report(
    db: Session,
    screening_id: int,
):
    result = get_screening_result(
        db=db,
        screening_id=screening_id,
    )

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=20,
        spaceAfter=20,
    )

    heading_style = ParagraphStyle(
        "ReportHeading",
        parent=styles["Heading2"],
        fontSize=14,
        spaceBefore=15,
        spaceAfter=8,
    )

    normal_style = ParagraphStyle(
        "ReportNormal",
        parent=styles["Normal"],
        fontSize=10,
        leading=15,
    )

    story = []

    story.append(
        Paragraph(
            "AI Resume Screening Report",
            title_style,
        )
    )

    story.append(
        Spacer(1, 10)
    )

    candidate_name = (
        result.user.name
        if result.user
        else "Not available"
    )

    job_title = (
        result.job.job_title
        if result.job
        else "Not available"
    )

    experience = (
        result.resume.experience
        if result.resume
        else None
    )

    qualification = (
        result.resume.qualification
        if result.resume
        else None
    )

    certifications = (
        result.resume.certifications
        if result.resume
        else []
    )

    details = [
        [
            "Candidate",
            escape(_format_value(candidate_name)),
        ],
        [
            "Job Title",
            escape(_format_value(job_title)),
        ],
        [
            "Match Score",
            f"{result.match_score if result.match_score is not None else 0}%",
        ],
        [
            "Screening Result",
            escape(_format_value(result.screening_result)),
        ],
        [
            "Experience",
            escape(_format_value(experience)),
        ],
        [
            "Qualification",
            escape(_format_value(qualification)),
        ],
        [
            "Certifications",
            escape(_format_value(certifications)),
        ],
    ]

    details_table = Table(
        details,
        colWidths=[130, 350],
    )

    details_table.setStyle(
        TableStyle(
            [
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.lightgrey,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
            ]
        )
    )

    story.append(details_table)

    story.append(
        Paragraph(
            "Matched Skills",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            escape(
                _format_value(
                    result.matched_skills
                )
            ),
            normal_style,
        )
    )

    story.append(
        Paragraph(
            "Missing Skills",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            escape(
                _format_value(
                    result.missing_skills
                )
            ),
            normal_style,
        )
    )

    story.append(
        Paragraph(
            "Experience Assessment",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            escape(
                _format_value(
                    result.experience_assessment
                )
            ),
            normal_style,
        )
    )

    story.append(
        Paragraph(
            "Qualification Assessment",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            escape(
                _format_value(
                    result.qualification_assessment
                )
            ),
            normal_style,
        )
    )

    story.append(
        Paragraph(
            "Strengths",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            escape(
                _format_value(
                    result.strengths
                )
            ),
            normal_style,
        )
    )

    story.append(
        Paragraph(
            "Concerns",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            escape(
                _format_value(
                    result.concerns
                )
            ),
            normal_style,
        )
    )

    story.append(
        Paragraph(
            "Score Breakdown",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            escape(
                _format_value(
                    result.score_breakdown
                )
            ),
            normal_style,
        )
    )

    story.append(
        Paragraph(
            "Recommendation",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            escape(
                _format_value(
                    result.recommendation
                )
            ),
            normal_style,
        )
    )

    story.append(
        Paragraph(
            "Summary",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            escape(
                _format_value(
                    result.screening_result
                )
            ),
            normal_style,
        )
    )

    document.build(story)

    buffer.seek(0)

    return buffer