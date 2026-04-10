import os
import sys
from pprint import pprint

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from app.connectors.clinicaltrials import ClinicalTrialsConnector

def main():
    connector = ClinicalTrialsConnector()
    docs = connector.fetch_trials(
        query="breast cancer trastuzumab",
        max_documents=2
    )

    print(f"Fetched {len(docs)} documents")

    for i, doc in enumerate(docs, 1):
        print(f"\n--- Document {i} ---")
        pprint(doc)

if __name__ == "__main__":
    main()