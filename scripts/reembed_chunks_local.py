import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from app.db.session import SessionLocal
from app.db.models import Chunk
from app.services.embedding_service import EmbeddingService

def main():
    db = SessionLocal()
    embedding_service = EmbeddingService()

    try:
        chunks = db.query(Chunk).all()
        print(f"Found {len(chunks)} chunks to re-embed")

        if not chunks:
            print("No chunks found")
            return

        texts = [chunk.content for chunk in chunks]
        vectors = embedding_service.embed_documents(texts)

        for chunk, vector in zip(chunks, vectors):
            chunk.embedding = vector

        db.commit()
        print(f"Successfully re-embedded {len(chunks)} chunks")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()