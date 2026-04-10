import os
import sys
from pprint import pprint

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from app.services.query_service import QueryService

def main():
    service = QueryService()

    question = "What primary outcomes are being measured in HER2-positive breast cancer trials?"

    result1 = service.answer_question(question=question, top_k=3)
    print("\nFIRST CALL")
    pprint(result1)

    result2 = service.answer_question(question=question, top_k=3)
    print("\nSECOND CALL (should be cached)")
    pprint(result2)

if __name__ == "__main__":
    main()