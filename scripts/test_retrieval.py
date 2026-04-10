import os
import sys
from pprint import pprint

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from app.services.retrieval_service import RetrievalService


def main():
    service = RetrievalService()

    # Test with your ingested data
    chunks = service.retrieve(
        question="What clinical trials are studying HER2 positive breast cancer?",
        top_k=3,
    )

    print(f"Retrieved {len(chunks)} chunks")
    for i, chunk in enumerate(chunks, 1):
        print(f"\n--- Chunk {i} (distance: {chunk['distance']:.3f}) ---")
        print(f"Source: {chunk['source_type']} | {chunk['title'][:60]}...")
        print(f"Content preview: {chunk['content'][:150]}...")
        print(f"URL: {chunk['source_url']}")


if __name__ == "__main__":
    main()