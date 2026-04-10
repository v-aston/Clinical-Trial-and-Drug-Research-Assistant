from sqlalchemy import select, text
from app.db.session import SessionLocal
from app.db.models import Chunk, SourceDocument
from app.services.embedding_service import EmbeddingService

class RetrievalService:
    def __init__(self):
        self.embedding_service = EmbeddingService()

    def retrieve(self, question: str, top_k: int = 5):
        query_vector = self.embedding_service.embed_query(question)

        db = SessionLocal()
        try:
            stmt = (
                select(
                    Chunk.id,
                    Chunk.document_id,
                    Chunk.chunk_index,
                    Chunk.section,
                    Chunk.content,
                    Chunk.metadata_json,
                    SourceDocument.title,
                    SourceDocument.source_type,
                    SourceDocument.source_url,
                    Chunk.embedding.cosine_distance(query_vector).label("distance")
                )
                .join(SourceDocument, SourceDocument.id == Chunk.document_id)
                .where(Chunk.embedding.is_not(None))
                .order_by(text("distance ASC"))
                .limit(top_k)
            )

            rows = db.execute(stmt).all()

            results = []
            for row in rows:
                distance = float(row.distance)
                if distance > 0.7:
                    continue

                results.append({
                    "chunk_id": row.id,
                    "document_id": row.document_id,
                    "chunk_index": row.chunk_index,
                    "section": row.section,
                    "content": row.content,
                    "metadata_json": row.metadata_json,
                    "title": row.title,
                    "source_type": row.source_type,
                    "source_url": row.source_url,
                    "distance": float(row.distance),
                })

            return results
        finally:
            db.close()