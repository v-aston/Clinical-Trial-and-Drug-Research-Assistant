from typing import List, Dict
from app.rag.chunking import chunk_text
from app.utils.ids import new_id

class ChunkingService:
    def build_chunks_for_document(self, document) -> List[Dict]:
        chunks = chunk_text(document.raw_text or "")
        chunk_rows = []

        for idx, chunk in enumerate(chunks):
            chunk_rows.append({
                "id": new_id("chunk"),
                "document_id": document.id,
                "chunk_index": idx,
                "section": None,
                "content": chunk,
                "metadata_json": {
                    **(document.metadata_json or {}),
                    "source_type": document.source_type,
                    "external_id": document.external_id,
                    "title": document.title,
                },
                "embedding": None,
            })

        return chunk_rows