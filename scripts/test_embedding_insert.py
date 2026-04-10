import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from app.db.session import SessionLocal
from app.db.models import Chunk
from app.services.embedding_service import EmbeddingService

def main():
    db = SessionLocal()
    service = EmbeddingService()

    try:
        chunks = db.query(Chunk).filter(Chunk.embedding.is_(None)).all()
        print(f"Found {len(chunks)} chunks without embeddings")

        if not chunks:
            print("No chunks to embed.")
            return

        texts = [chunk.content for chunk in chunks]
        vectors = service.embed_documents(texts)

        for chunk, vector in zip(chunks, vectors):
            chunk.embedding = vector

        db.commit()

        updated = db.query(Chunk).filter(Chunk.embedding.is_not(None)).count()
        print(f"Embeddings stored for {updated} chunks")
    finally:
        db.close()

if __name__ == "__main__":
    main()