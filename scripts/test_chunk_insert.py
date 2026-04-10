import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from app.db.session import SessionLocal
from app.db.models import SourceDocument, Chunk
from app.services.chunking_service import ChunkingService
from app.utils.ids import new_id

def main():
    db = SessionLocal()
    service = ChunkingService()
    total_chunks = 0

    try:
        docs = db.query(SourceDocument).all()

        for doc in docs:
            existing_chunks = db.query(Chunk).filter(Chunk.document_id == doc.id).count()
            if existing_chunks > 0:
                print(f"Skipping {doc.id}, already has {existing_chunks} chunks")
                continue

            chunk_rows = service.build_chunks_for_document(doc)

            for row in chunk_rows:
                db.add(Chunk(**row))

            total_chunks += len(chunk_rows)
            print(f"{doc.id}: created {len(chunk_rows)} chunks")

        db.commit()

        print(f"Inserted total chunks: {total_chunks}")
        print(f"Total chunk rows in DB: {db.query(Chunk).count()}")
    finally:
        db.close()

if __name__ == "__main__":
    main()