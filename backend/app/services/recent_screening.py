from app.dto.recent_screening import RecentScreeningResponse


def get_recent_screenings() -> RecentScreeningResponse:

    return RecentScreeningResponse(
        message="Recent screening results",
        data={
            "recent_screenings": [
                {
                    "screening_id": 1,
                    "candidate": "John Doe",
                    "job_title": "AI Full Stack Developer",
                    "match_score": 85.5,
                    "status": "Selected",
                    "date": "2026-08-29"
                }
            ]
        }
    )