import os
import sys
from pprint import pprint

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from app.services.query_service import QueryService

def main():
    service = QueryService()

    result = service.answer_question(
        question="What primary outcomes are being measured in HER2-positive breast cancer trials?",
        top_k=3
    )

    print("\n=== ANSWER ===\n")
    print(result["answer"])

    print("\n=== CITATIONS ===\n")
    pprint(result["citations"])

if __name__ == "__main__":
    main()