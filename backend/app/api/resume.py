from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    HTTPException
)

from sqlalchemy.orm import Session

from app.models.database import get_db

from app.ai.extraction.resume_extractor import (
    extract_resume_text
)

from app.services.resume_service import (
    process_resume
)



router = APIRouter(
    prefix="/resume",
    tags=["Resume"]
)


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    try:

      
        allowed_extensions = [
            ".pdf",
            ".docx",
            ".doc"
        ]

        file_name = file.filename or ""

        extension = (
            "." + file_name.split(".")[-1].lower()
        )

        if extension not in allowed_extensions:

            raise HTTPException(
                status_code=400,
                detail="Only PDF, DOC and DOCX files are allowed."
            )

        
        file_content = await file.read()

        upload_directory = "uploads"

        import os

        os.makedirs(
            upload_directory,
            exist_ok=True
        )

        file_path = os.path.join(
            upload_directory,
            file_name
        )

        with open(
            file_path,
            "wb"
        ) as output_file:

            output_file.write(
                file_content
            )

        
        resume_text = extract_resume_text(
            file_path
        )

        
        result = process_resume(
            db=db,
            user_id=1,
            file_name=file_name,
            file_path=file_path,
            resume_text=resume_text
        )

        
        return {
            "message": "Resume uploaded and processed successfully",
            "data": result
        }

    except HTTPException:
        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )