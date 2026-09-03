from app.ai.extraction.resume_extractor import (
    extract_resume_text
)

from app.ai.resume.resume_parser import (
    parse_resume
)


FILE_PATH = "test_resume.pdf"


try:

    # Extract resume
    resume_text = extract_resume_text(
        FILE_PATH
    )

    print(
        "\n========== EXTRACTED RESUME ==========\n"
    )

    print(resume_text)

    # Parse using Groq
    resume_data = parse_resume(
        resume_text
    )

    print(
        "\n========== GROQ RESULT ==========\n"
    )

    print(
        resume_data.model_dump_json(
            indent=4
        )
    )

except Exception as error:

    print(
        "\n========== ERROR ==========\n"
    )

    print(error)