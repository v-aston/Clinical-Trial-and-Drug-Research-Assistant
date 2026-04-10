from app.connectors.clinicaltrials import ClinicalTrialsConnector
from app.connectors.pubmed import PubMedConnector
from app.db.session import SessionLocal
from app.db.models import SourceDocument, Chunk
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.utils.ids import new_id

class IngestService:
    def __init__(self):
        self.clinicaltrials_connector = ClinicalTrialsConnector()
        self.pubmed_connector = PubMedConnector()
        self.chunking_service = ChunkingService()
        self.embedding_service = EmbeddingService()

    def ingest(self, source_type: str, query: str, max_documents: int = 5) -> dict:
        db = SessionLocal()

        try:
            # 1. Fetch docs from connector
            if source_type == "clinicaltrials":
                raw_docs = self.clinicaltrials_connector.fetch_trials(
                    query=query,
                    max_documents=max_documents
                )
            elif source_type == "pubmed":
                raw_docs = self.pubmed_connector.search(
                    query=query,
                    max_documents=max_documents
                )
            else:
                raise ValueError(f"Unsupported source_type: {source_type}")

            documents_fetched = len(raw_docs)
            documents_inserted = 0
            chunks_created = 0
            embeddings_created = 0

            new_chunks = []

            # 2. Insert only new documents
            for doc in raw_docs:
                existing = (
                    db.query(SourceDocument)
                    .filter(
                        SourceDocument.source_type == doc["source_type"],
                        SourceDocument.external_id == doc["external_id"]
                    )
                    .first()
                )

                if existing:
                    continue

                db_doc = SourceDocument(
                    id=new_id("doc"),
                    external_id=doc["external_id"],
                    source_type=doc["source_type"],
                    title=doc["title"],
                    source_url=doc["source_url"],
                    raw_text=doc["raw_text"],
                    metadata_json=doc["metadata_json"],
                )
                db.add(db_doc)
                db.flush()

                documents_inserted += 1

                # 3. Chunk this new document
                chunk_rows = self.chunking_service.build_chunks_for_document(db_doc)

                for row in chunk_rows:
                    chunk_obj = Chunk(**row)
                    db.add(chunk_obj)
                    new_chunks.append(chunk_obj)

                chunks_created += len(chunk_rows)

            db.flush()

            # 4. Generate embeddings only for newly created chunks
            if new_chunks:
                texts = [chunk.content for chunk in new_chunks]
                vectors = self.embedding_service.embed_documents(texts)

                for chunk, vector in zip(new_chunks, vectors):
                    chunk.embedding = vector

                embeddings_created = len(new_chunks)

            db.commit()

            return {
                "status": "success",
                "source_type": source_type,
                "query": query,
                "documents_fetched": documents_fetched,
                "documents_inserted": documents_inserted,
                "chunks_created": chunks_created,
                "embeddings_created": embeddings_created,
            }

        except Exception:
            db.rollback()
            raise
        finally:
            db.close()