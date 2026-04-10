import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from app.services.embedding_service import EmbeddingService

def main():
    service = EmbeddingService()
    vector = service.embed_query("What are the primary outcomes in HER2-positive breast cancer trials?")

    print(f"Embedding length: {len(vector)}")
    print(vector[:10])

if __name__ == "__main__":
    main()