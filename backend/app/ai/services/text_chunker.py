from __future__ import annotations


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[str]:
    """Split text into overlapping chunks while preserving word boundaries."""

    if not text or not text.strip():
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be between zero and chunk_size - 1"
        )

    normalized_text = " ".join(text.split())

    chunks: list[str] = []
    start = 0

    while start < len(normalized_text):
        end = min(start + chunk_size, len(normalized_text))

        # Try to end the chunk at a word boundary.
        if end < len(normalized_text):
            boundary = normalized_text.rfind(" ", start, end)

            if boundary > start:
                end = boundary

        chunk = normalized_text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(normalized_text):
            break

        # Move backward from the current end to maintain overlap.
        next_start = end - chunk_overlap

        # Safety check to avoid getting stuck.
        if next_start <= start:
            next_start = end

        start = next_start

    return chunks