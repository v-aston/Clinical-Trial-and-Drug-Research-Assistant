import os
import sys
from pprint import pprint

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from app.services.ingest_service import IngestService

def main():
    service = IngestService()

    result = service.ingest(
        source_type="clinicaltrials",
        query="HER2 positive breast cancer",
        max_documents=2,
    )

    pprint(result)

if __name__ == "__main__":
    main()