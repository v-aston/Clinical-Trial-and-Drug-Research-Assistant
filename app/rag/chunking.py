from typing import List

def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 150) -> List[str]:
    clean = " ".join((text or "").split())
    if not clean:
        return []

    chunks = []
    start = 0

    while start < len(clean):
        end = min(len(clean), start + chunk_size)
        chunks.append(clean[start:end])

        if end >= len(clean):
            break

        start = max(0, end - overlap)

    return chunks