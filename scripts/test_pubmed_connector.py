import os
import sys
from pprint import pprint

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from app.connectors.pubmed import PubMedConnector

def main():
    connector = PubMedConnector()
    docs = connector.search("HER2 positive breast cancer", max_documents=2)

    print(f"Fetched {len(docs)} documents")
    for i, doc in enumerate(docs, 1):
        print(f"\n--- Document {i} ---")
        pprint(doc)

if __name__ == "__main__":
    main()