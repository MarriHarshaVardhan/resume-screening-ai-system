import re


def clean_resume_text(text: str) -> str:
    """
    Clean and normalize extracted resume text.
    """

    if not text:
        return ""

    # Normalize Windows and old-style line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Replace tabs with spaces
    text = text.replace("\t", " ")

    # Remove repeated spaces
    text = re.sub(
        r"[ ]{2,}",
        " ",
        text
    )

    # Remove spaces around new lines
    text = re.sub(
        r" *\n *",
        "\n",
        text
    )

    # Limit repeated empty lines to a maximum of one empty line
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    # Remove non-printable control characters
    text = re.sub(
        r"[^\x09\x0A\x0D\x20-\x7E]",
        " ",
        text
    )

    # Normalize spaces again after character cleanup
    text = re.sub(
        r"[ ]{2,}",
        " ",
        text
    )

    return text.strip()