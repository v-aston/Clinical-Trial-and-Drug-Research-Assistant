import os
import sys
from pprint import pprint

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from app.db.session import SessionLocal
from app.db.models import SourceDocument
from app.connectors.clinicaltrials import ClinicalTrialsConnector
from app.utils.ids import new_id

def main():
    connector = ClinicalTrialsConnector()
    docs = connector.fetch_trials("breast cancer trastuzumab", max_documents=2)

    db = SessionLocal()
    inserted = 0

    try:
        for d in docs:
            existing = db.query(SourceDocument).filter(
                SourceDocument.source_type == d["source_type"],
                SourceDocument.external_id == d["external_id"]
            ).first()

            if existing:
                print(f"Skipping existing: {d['external_id']}")
                continue

            row = SourceDocument(
                id=new_id("doc"),
                source_type=d["source_type"],
                external_id=d["external_id"],
                title=d["title"],
                source_url=d["source_url"],
                raw_text=d["raw_text"],
                metadata_json=d["metadata_json"],
            )
            db.add(row)
            inserted += 1

        db.commit()
        print(f"Inserted {inserted} documents")

        rows = db.query(SourceDocument).all()
        print(f"Total rows in source_documents: {len(rows)}")
        for row in rows:
            pprint({
                "id": row.id,
                "external_id": row.external_id,
                "title": row.title,
                "source_type": row.source_type
            })
    finally:
        db.close()

if __name__ == "__main__":
    main()